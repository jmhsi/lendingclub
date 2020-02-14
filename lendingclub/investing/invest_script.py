'''
Script to run every time there is an investment round
'''
import os
import sys
import argparse
import requests
import math
import datetime
import timeit
import pytz
import pickle
import json
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
# trying to embed matplotlib plots into emails
from email.message import EmailMessage
from email.utils import make_msgid
import mimetypes

# LC imports
import user_creds.account_info as acc_info
from lendingclub.investing import investing_utils as inv_util
from lendingclub.modeling import score_utils as scr_util
from lendingclub import config
from lendingclub.modeling.models import Model

parser = argparse.ArgumentParser()
parser.add_argument('--test', '-t', help='Boolean, if True will invest fast and not wait', action='store_true')
args = parser.parse_args()
test = args.test
    
def handle_new_cols_to_sql(df, table_name, con):
    '''
    If new columns are added, bring in existing sql table and combine with
    pandas, then rewrite out new dataframe
    '''
    try:
        #this will fail if there is a new column
        df.to_sql(name=table_name, con=con, if_exists = 'append', index=False)
    except sqlalchemy.exc.OperationalError:
        data = pd.read_sql(f'SELECT * FROM {table_name}', con)
        df2 = pd.concat([data,df])
        df2.to_sql(name=table_name, con=con, if_exists = 'replace', index=False)
    

# lendingclub account + API related constants
inv_amt = 250.00
cash_limit = 0.00

token = acc_info.token
inv_acc_id = acc_info.investor_id
portfolio_id = acc_info.portfolio_id
my_gmail_account = acc_info.from_email_throwaway
my_gmail_password = acc_info.password_throwaway
my_recipients = acc_info.to_emails_throwaway
header = {
    'Authorization': token,
    'Content-Type': 'application/json',
    'X-LC-LISTING-VERSION': '1.3'
}
acc_summary_url = 'https://api.lendingclub.com/api/investor/v1/accounts/' + \
    str(inv_acc_id) + '/summary'
order_url = 'https://api.lendingclub.com/api/investor/v1/accounts/' + \
    str(inv_acc_id) + '/orders'

# check account money, how much money to deploy in loans
summary_dict = json.loads(requests.get(
    acc_summary_url, headers=header).content)
cash_to_invest = summary_dict['availableCash']
n_to_pick = int(math.floor(cash_to_invest / inv_amt))

# other constants
western = pytz.timezone('US/Pacific')
now = datetime.datetime.now(tz=pytz.UTC)


# setup for model
with open(os.path.join(config.data_dir, 'base_loan_info_dtypes.pkl'), 'rb') as f:
    base_loan_dtypes = pickle.load(f)
cb_both = Model('catboost_both')
# clf_wt_scorer will combine the regr and clf scores, with clf wt of 20%
clf_wt_scorer = scr_util.combined_score(scr_util.clf_wt)

# WAIT UNTIL LOANS RELEASED. I'm rate limited to 1 call a second
inv_util.pause_until_time(test=test)    

# Start timings
start = timeit.default_timer()

# get loans from API, munge them to a form that matches training data
api_loans, api_ids = inv_util.get_loans_and_ids(
    header, exclude_already=True)

# time for getting loans
t1 = timeit.default_timer()

# match format of cr_line dates and emp_length, dti, dti_joint
api_loans['earliest_cr_line'] = pd.to_datetime(api_loans['earliest_cr_line'].str[:10])
api_loans['sec_app_earliest_cr_line'] = pd.to_datetime(api_loans['sec_app_earliest_cr_line'].str[:10])
bins = [12*k for k in range(1,11)]
bins = [-np.inf] + bins + [np.inf]
labels = ['< 1 year','1 year','2 years','3 years','4 years','5 years','6 years','7 years','8 years','9 years','10+ years',]
api_loans['emp_length'] = pd.cut(api_loans['emp_length'], bins=bins, labels=labels, right=False).astype(str).replace({'nan':'None'})
# I think 9999 is supposed to be their value for nan. Not entirely sure
api_loans['dti'] = api_loans['dti'].replace({9999:np.nan})
api_loans['dti_joint'] = api_loans['dti_joint'].replace({9999:np.nan})
api_loans = api_loans.astype(base_loan_dtypes)

# time for finishing munging data to correct form
t2 = timeit.default_timer()

# make raw scores and combined scores
_, api_loans['catboost_regr'], api_loans['catboost_clf'] = cb_both.score(api_loans, return_all=True)
api_loans['catboost_regr_scl'] = scr_util.scale_cb_regr_score(api_loans)
catboost_comb_col = f'catboost_comb_{int(scr_util.clf_wt*100)}'
api_loans[catboost_comb_col] = clf_wt_scorer('catboost_clf', 'catboost_regr_scl', api_loans)

# time for finishing the entire scorer
t3 = timeit.default_timer()

# get loans that pass the investing criteria
investable_loans = api_loans.query(f"{catboost_comb_col} >= {scr_util.min_comb_score}")
# investable_loans = investable_loans.sort_values('catboost_comb', ascending=False)

# time for getting investable loans
t4 = timeit.default_timer()

# Set up order and submit order
to_order_loan_ids = investable_loans.nlargest(n_to_pick, catboost_comb_col)['id']
orders_dict = {'aid': inv_acc_id}
orders_list = [{'loanId': int(loan_ids),
                        'requestedAmount': int(inv_amt),
                        'portfolioId': int(portfolio_id)} for loan_ids in to_order_loan_ids]
orders_dict['orders'] = orders_list
payload = json.dumps(orders_dict)
# place order
order_resp = inv_util.submit_lc_order(cash_to_invest, cash_limit, order_url, header, payload)

# time for assembling and placing orders
t5 = timeit.default_timer()

# some date related columns to add before writing to db
# convert existing date cols
to_datify = [col for col in api_loans.columns if '_d' in col and api_loans[col].dtype == 'object']
for col in to_datify:
    api_loans[col] = pd.to_datetime(api_loans[col], utc=True).dt.tz_convert(western)

# add date cols: date, year, month, week of year, day, hour
api_loans['last_seen_list_d'] = now
api_loans['list_d_year'] = api_loans['list_d'].dt.year
api_loans['list_d_month'] = api_loans['list_d'].dt.month
api_loans['list_d_day'] = api_loans['list_d'].dt.day
api_loans['list_d_week'] = api_loans['list_d'].dt.week
api_loans['list_d_hour'] = api_loans['list_d'].dt.hour
api_loans['last_seen_list_d_year'] = api_loans['last_seen_list_d'].dt.year
api_loans['last_seen_list_d_month'] = api_loans['last_seen_list_d'].dt.month
api_loans['last_seen_list_d_day'] = api_loans['last_seen_list_d'].dt.day
api_loans['last_seen_list_d_week'] = api_loans['last_seen_list_d'].dt.week
api_loans['last_seen_list_d_hour'] = api_loans['last_seen_list_d'].dt.hour

msg = EmailMessage()
order_time = now.strftime("%Y-%m-%d %H:%M:%S.%f")
# email headers
email_cols = ['id', 'int_rate', 'term', 'catboost_clf', 'catboost_regr', 'catboost_regr_scl', catboost_comb_col]
msg['Subject'] = order_time + ' Investment Round'
msg['From'] = 'justindlrig <{0}>'.format(my_gmail_account)
msg['To'] = 'self <{0}>'.format(my_recipients[0])
# set the plain text body
msg_content = f"investment round \n LC API Response: {order_resp} \n Response Contents: {order_resp.content} \
\n Time to get loans: {t1 - start} \n Time to munge loans: {t2 - t1} \n Time to finish scoring process: {t3 - t2} \
\n Time to get investable loans: {t4 - t3} \n Time to assemble and place order {t5 - t4} \
\n Time whole process {t5 - start} \n {investable_loans[email_cols]} \n {api_loans[email_cols]}"
msg.set_content(msg_content)

inv_util.send_emails(now, my_gmail_account, my_gmail_password, msg)

# make the timing_df
timing_df = pd.DataFrame({'start': start,
                          'api_get_loans': t1 - start,
                          'munge_api_loans': t2 - t1,
                          'finish_scoring': t3 - t2,
                          'get_investable': t4 - t3,
                          'assemble_place_order': t5 - t4,
                          'order_date': order_time,
                          'whole_process': t5 - start,
}, index=[0])

# write dataframes out to db
disk_engine = create_engine(f'sqlite:///{config.lc_api_db}')
handle_new_cols_to_sql(api_loans, 'lc_api_loans', disk_engine)
handle_new_cols_to_sql(timing_df, 'order_timings', disk_engine)
#api_loans.to_sql('lc_api_loans', disk_engine, if_exists='append', index=False,)
#timing_df.to_sql('order_timings', disk_engine, if_exists='append', index=False,)
