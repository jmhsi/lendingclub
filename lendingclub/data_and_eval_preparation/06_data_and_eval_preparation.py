'''
renames loan_info to match what is received through the api
makes a scaled pmt_history and other various targets for evaluation of models
'''

import os

import numpy as np
# %load ../../lendingclub/data_and_eval_preparation/data_and_eval_preparation.py
import pandas as pd
from tqdm import tqdm

# import gspread
# from google.oauth2 import service_account
# from google.auth.transport.requests import AuthorizedSession
import j_utils.munging as mg
import lendingclub.config as config
import lendingclub.investing.investing_utils as investing_utils
# custom imports
import user_creds.account_info as acc_info

# set paths
ppath = config.prj_dir
dpath = config.data_dir

# load in dataframes
loan_info = pd.read_feather(os.path.join(dpath, 'clean_loan_info.fth'))
pmt_hist = pd.read_feather(os.path.join(dpath, 'clean_pmt_history.fth'))
strings = pd.read_feather(os.path.join(dpath, 'strings_loan_info.fth'))
strings = strings[strings['id'].isin(loan_info['id'])]

# sort rows by loan_id (and date)
loan_info = loan_info.sort_values('id')
pmt_hist = pmt_hist.sort_values(['loan_id', 'date'])
strings = strings.sort_values('id')

# rename loan_id to id to match what comes through API
pmt_hist = pmt_hist.rename({'loan_id': 'id'}, axis=1)

# check how fields come in through API _______________________________________
# constants and setup for various accounts and APIs
token = acc_info.token
inv_acc_id = acc_info.investor_id
portfolio_id = acc_info.portfolio_id
header = {
    'Authorization': token,
    'Content-Type': 'application/json',
    'X-LC-LISTING-VERSION': '1.3'
}

# get the loans and process the dataframe
_, all_loan_count = investing_utils.get_loans_and_ids(
    header, exclude_already=False)
api_loans, api_ids = investing_utils.get_loans_and_ids(
    header, exclude_already=True)

# checking the fields from csv vs API
api_flds = set(api_loans.columns)
licsv_flds = set(loan_info.columns)
common_flds = api_flds.intersection(licsv_flds)
api_flds_not_in_licsv = api_flds.difference(licsv_flds)
licsv_flds_not_in_api = licsv_flds.difference(api_flds)

# rename some loan_info fields to match those coming through api
licsv_to_api_rename_dict = {
    'acc_open_past_24mths':'acc_open_past_24_mths',
    'zip_code': 'addr_zip',
    'delinq_2yrs': 'delinq_2_yrs',
    'funded_amnt': 'funded_amount',
    'il_util': 'i_l_util',
    'inq_last_6mths': 'inq_last_6_mths',
#     'installment_at_funded': 'installment',
    'verification_status': 'is_inc_v',
    'verification_status_joint': 'is_inc_v_joint',
    'loan_amnt': 'loan_amount',
    'num_accts_ever_120_pd': 'num_accts_ever_12_0_ppd',
    'num_tl_120dpd_2m': 'num_tl_12_0dpd_2m',
    'sec_app_inq_last_6mths': 'sec_app_inq_last_6_mths',
}
loan_info.rename(licsv_to_api_rename_dict, axis=1, inplace=True)

# SAVE this version of loan info
loan_info.reset_index(drop=True, inplace=True)
loan_info.to_feather(os.path.join(dpath, 'clean_loan_info_api_name_matched.fth'))

# split loan info into dataframes for training off of and evaluating__________
eval_flds = ['end_d', 'issue_d', 'maturity_paid', 'maturity_time', 'maturity_time_stat_adj', 'maturity_paid_stat_adj', 'rem_to_be_paid', 'roi_simple',
             'target_loose', 'target_strict', 'loan_status', 'id']
strb_flds = ['desc', 'emp_title', 'id']
base_loan_info = loan_info[list(common_flds)]
eval_loan_info = loan_info[eval_flds + ['grade']]
str_loan_info = strings[strb_flds]

# SAVE
base_loan_info.to_feather(os.path.join(dpath, 'base_loan_info.fth'))
# save it at bottom of script
# eval_loan_info.to_feather(os.path.join(dpath, 'eval_loan_info.fth'))
# str_loan_info.reset_index(drop=True, inplace=True)
# str_loan_info.to_feather(os.path.join(dpath, 'str_loan_info.fth'))

# make a version of pmt_history where each loan is scaled to be equal size____
pmt_hist = pmt_hist[pmt_hist['id'].isin(loan_info['id'])]
loan_funded_amts = loan_info.set_index('id')['funded_amount'].to_dict()
loan_dollar_cols = [
    'outs_princp_beg',
    'princp_paid',
    'int_paid',
    'fee_paid',
    'amt_due',
    'amt_paid',
    'outs_princp_end',
    'charged_off_amt',
    'monthly_pmt',
    'recovs',
    'recov_fees',
    'all_cash_to_inv', ]
id_grouped = pmt_hist.groupby('id', sort=False)
funded_amts = []
for ids, group in tqdm(id_grouped):
    funded_amt = loan_funded_amts[ids]
    funded_amts.extend([funded_amt]*len(group))    
for col in loan_dollar_cols:
    pmt_hist[col] = pmt_hist[col]/funded_amts
    

# make npv_rois (using various discount rates and actual/known cashflows)_____
interesting_cols_over_time = [
    'outs_princp_beg',
    'all_cash_to_inv',
    'date',
    'fico_last',
    'm_on_books',
    'status_period_end',
    'id',
]
pmt_hist = pmt_hist[interesting_cols_over_time]
npv_roi_holder = {}
disc_rates = np.arange(.05,.36,.01)
id_grouped = pmt_hist.groupby('id')
for ids, group in tqdm(id_grouped):
    npv_roi_dict = {}
    funded = group.iat[0,0]
    cfs = [-funded] + group['all_cash_to_inv'].tolist()
    for rate in disc_rates:
        npv_roi_dict[rate] = np.npv(rate/12, cfs)/funded
    npv_roi_holder[ids] = npv_roi_dict
    
npv_roi_df = pd.DataFrame(npv_roi_holder).T
npv_roi_df.columns = npv_roi_df.columns.values.round(2)
npv_roi_df.index.name = 'id'
npv_roi_df.reset_index(inplace=True)

eval_loan_info = pd.merge(eval_loan_info, npv_roi_df, how='left', on='id')
# some current loans I have no target_strict for and were not in pmt history.
# Fill with negatives on npv_roi.
eval_loan_info['target_strict'] = eval_loan_info['target_strict'].fillna(0)
eval_loan_info.fillna(-1, inplace=True)



# SAVE
pmt_hist.reset_index(drop=True, inplace=True)
_, pmt_hist = mg.reduce_memory(pmt_hist)
pmt_hist.to_feather(os.path.join(dpath,'scaled_pmt_hist.fth'))

# SAVE
# feather must have string column names
eval_loan_info.columns = [str(col) for col in eval_loan_info.columns]
eval_loan_info.to_feather(os.path.join(dpath, 'eval_loan_info.fth'))
