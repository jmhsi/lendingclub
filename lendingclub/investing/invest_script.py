'''
Script to run every time there is an investment round
'''
import os
import sys
import argparse
import requests
import math
import datetime
import pytz
import pickle
import json
import numpy as np
import pandas as pd
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
    
# print(test)
# print(type(test))
    

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
now = datetime.datetime.now(pytz.FixedOffset(-480))


# setup for model
with open(os.path.join(config.data_dir, 'base_loan_info_dtypes.pkl'), 'rb') as f:
    base_loan_dtypes = pickle.load(f)
cb_both = Model('catboost_both')
# clf_wt_scorer will combine the regr and clf scores, with clf wt of 20%
clf_wt_scorer = scr_util.combined_score(scr_util.clf_wt)

# WAIT UNTIL LOANS RELEASED. I'm rate limited to 1 call a second
inv_util.pause_until_time(test=test)    

# get loans from API, munge them to a form that matches training data
api_loans, api_ids = inv_util.get_loans_and_ids(
    header, exclude_already=True)
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

# make raw scores and combined scores
_, api_loans['catboost_regr'], api_loans['catboost_clf'] = cb_both.score(api_loans, return_all=True)
api_loans['catboost_regr_scl'] = scr_util.scale_cb_regr_score(api_loans)
catboost_comb_col = f'catboost_comb_{int(scr_util.clf_wt*100)}'
api_loans[catboost_comb_col] = clf_wt_scorer('catboost_clf', 'catboost_regr_scl', api_loans)

# get loans that pass the investing criteria
investable_loans = api_loans.query(f"{catboost_comb_col} >= {scr_util.min_comb_score}")
# investable_loans = investable_loans.sort_values('catboost_comb', ascending=False)

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

# some date related columns to add before writing to db
# convert existing date cols
to_datify = [col for col in api_loans.columns if '_d' in col and api_loans[col].dtype == 'object']
for col in to_datify:
    api_loans[col] = pd.to_datetime(api_loans[col])
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
# email headers
email_cols = ['id', 'int_rate', 'term', 'catboost_clf', 'catboost_regr', 'catboost_regr_scl', catboost_comb_col]
msg['Subject'] = now.strftime("%Y-%m-%d %H:%M:%S.%f") + ' Investment Round'
msg['From'] = 'justindlrig <{0}>'.format(my_gmail_account)
msg['To'] = 'self <{0}>'.format(my_recipients[0])
# set the plain text body
msg.set_content("test investment round \n LC API Response: {0} \n Response Contents: {1} \n {2} \n {3}".format(order_resp, order_resp.content, investable_loans[email_cols], api_loans[email_cols]))
# now create a Content-ID for the image
image_cid = make_msgid(domain='xyz.com')#
# if `domain` argument isn't provided, it will 
# use your computer's name

# set an alternative html body
# msg.add_alternative("""\
# <html>
#     <body>
#         <p>This is an HTML body.<br>
#            It also has an image.
#         </p>
#         <img src="cid:{image_cid}">
#     </body>
# </html>
# """.format(image_cid=image_cid[1:-1]), subtype='html')
# # image_cid looks like <long.random.number@xyz.com>
# # to use it as the img src, we don't need `<` or `>`
# # so we use [1:-1] to strip them off
# with open('/home/justin/projects/nst_star_app/images/ex1.png', 'rb') as img:
#     # know the Content-Type of the image
#     maintype, subtype = mimetypes.guess_type(img.name)[0].split('/')
#     # attach it
#     msg.get_payload()[1].add_related(img.read(), 
#                                          maintype=maintype, 
#                                          subtype=subtype, 
#                                          cid=image_cid)
inv_util.send_emails(now, my_gmail_account, my_gmail_password, msg)


# write api_loans out to db
disk_engine = create_engine(f'sqlite:///{config.lc_api_db}')
api_loans.to_sql('lc_api_loans', disk_engine, if_exists='append', index=False)

# below for google account stuff

#google sheet keys
# invest_ss_key = acc_info.invest_ss_key
# investins_ss_key = acc_info.investins_ss_key


# creds = service_account.Credentials.from_service_account_file(os.path.join(config.prj_dir, 'user_creds', 'credentials.json'))
# scope = ['https://spreadsheets.google.com/feeds']
# creds = creds.with_scopes(scope)
# gc = gspread.Client(auth=creds)
# gc.session = AuthorizedSession(creds)
# sheet = gc.open_by_key(invest_ss_key).sheet1
# sheetins = gc.open_by_key(investins_ss_key).sheet1
