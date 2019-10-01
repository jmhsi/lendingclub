'''
Reads in payment history, does lots of cleaning
'''
import os
import pickle
import sys

import numpy as np
import pandas as pd
# %load ../../lendingclub/csv_preparation/clean_pmt_history_1.py
from tqdm import tqdm

import j_utils.munging as mg
from lendingclub import config


def find_dupe_dates(group):
    '''finds duplicated dates in groupby group'''
    return pd.to_datetime(group[group.duplicated('date')]['date'].values)

def merge_dupe_dates(group):
    '''
    Merges the releveant numeric columns in loans that have 2 entries
    for same month
    '''
    df_chunks = []
    dupe_dates = find_dupe_dates(group)
    df_chunks.append(group[~group['date'].isin(dupe_dates)])
    for date in dupe_dates:
        problem_rows = group[group['date'] == date]
        ori_index = problem_rows.index
        keep_row = problem_rows.iloc[-1].to_dict()
        keep_row['outs_princp_beg'] = problem_rows.loc[
            ori_index[0]].iloc[column_iloc_map['outs_princp_beg']]
        summed = problem_rows.sum()
        keep_row['princp_paid'] = summed['princp_paid']
        keep_row['int_paid'] = summed['int_paid']
        keep_row['fee_paid'] = summed['fee_paid']
        keep_row['amt_due'] = summed['amt_due']
        keep_row['amt_paid'] = summed['amt_paid']
        keep_row['charged_off_this_month'] = summed['charged_off_this_month']
        keep_row['charged_off_amt'] = summed['charged_off_amt']
        keep_row['recovs'] = summed['recovs']
        keep_row['recov_fees'] = summed['recov_fees']
        keep_row['all_cash_to_inv'] = summed['all_cash_to_inv']
        to_append = pd.DataFrame(keep_row, index=[ori_index[-1]])
        df_chunks.append(to_append)
    return pd.concat(df_chunks)


def find_closest_previous_record(ids, issue_d, first_date, actual_months, month):
    '''This function finds the closest previous month that is in the group.
    It is here to handle cases where a record of one month is missing, but the
    record before that missing month is also missing.'''
    offset = pd.DateOffset(months=-1)
    prev_month = month + offset
    if month < issue_d:
        print(ids)
        return first_date
    elif prev_month in actual_months:
        return prev_month
    return find_closest_previous_record(ids, issue_d, first_date, actual_months, prev_month)

csv_path = config.wrk_csv_dir
# for now its always been one csv. Will have to revisit if they break it out to multiple
pmt_hist_fnames = [f for f in os.listdir(csv_path) if 'PMTHIST' in f]
if len(pmt_hist_fnames) > 1:
    sys.exit('more than one payment history file')

# chunking for smaller development set
print('chunking for smaller dev set')
with open(os.path.join(config.data_dir, 'dev_ids.pkl'), "rb") as input_file:
    dev_ids = pickle.load(input_file)

reader = pd.read_csv(os.path.join(csv_path, pmt_hist_fnames[0]), chunksize=25000000)
pmt_hist = pd.concat([chunk.query('LOAN_ID in @dev_ids') for chunk in reader])

# pmt_hist_path = os.path.join(csv_path, pmt_hist_fnames[0])
# pmt_hist = pd.read_csv(pmt_hist_path,)
print("{:,}".format(len(pmt_hist)) + " rows of pmt_hist loaded")

# Compress memory
changed_type_cols, pmt_hist = mg.reduce_memory(pmt_hist)

# Set loan ids as int _____________________________________________________
pmt_hist['LOAN_ID'] = pmt_hist['LOAN_ID'].astype(int)
print('payment history for', len(pmt_hist['LOAN_ID'].unique()), 'different loan ids')

# Round values to 3 decimal places ____________________________________________
pmt_hist = pmt_hist.round(3)

# renaming columns ____________________________________________________________
rename_col_dict = {
    'LOAN_ID': 'loan_id',
    'PBAL_BEG_PERIOD': 'outs_princp_beg',
    'PRNCP_PAID': 'princp_paid',
    'INT_PAID': 'int_paid',
    'FEE_PAID': 'fee_paid',
    'DUE_AMT': 'amt_due',
    'RECEIVED_AMT': 'amt_paid',
    'RECEIVED_D': 'pmt_date',
    'PERIOD_END_LSTAT': 'status_period_end',
    'MONTH': 'date',
    'PBAL_END_PERIOD': 'outs_princp_end',
    'MOB': 'm_on_books',
    'CO': 'charged_off_this_month',
    'COAMT': 'charged_off_amt',
    'InterestRate': 'int_rate',
    'IssuedDate': 'issue_d',
    'MONTHLYCONTRACTAMT': 'monthly_pmt',
    'dti': 'dti',
    'State': 'addr_state',
    'HomeOwnership': 'home_ownership',
    'MonthlyIncome': 'm_income',
    'EarliestCREDITLine': 'first_credit_line',
    'OpenCREDITLines': 'open_credit_lines',
    'TotalCREDITLines': 'total_credit_lines',
    'RevolvingCREDITBalance': 'revol_credit_bal',
    'RevolvingLineUtilization': 'revol_line_util',
    'Inquiries6M': 'inq_6m',
    'DQ2yrs': 'dq_24m',
    'MonthsSinceDQ': 'm_since_dq',
    'PublicRec': 'public_recs',
    'MonthsSinceLastRec': 'm_since_rec',
    'EmploymentLength': 'emp_len',
    'currentpolicy': 'current_policy',
    'grade': 'grade',
    'term': 'term',
    'APPL_FICO_BAND': 'fico_apply',
    'Last_FICO_BAND': 'fico_last',
    'VINTAGE': 'vintage',
    'PCO_RECOVERY': 'recovs',
    'PCO_COLLECTION_FEE': 'recov_fees',
}

pmt_hist.rename(columns=rename_col_dict, inplace=True)

# There is a problem with the inquiries 6m column. Some are nan values and some
# are marked '*' with no explanation. inq6m should be in loan info so dropping
pmt_hist.drop('inq_6m', axis=1, inplace=True)

# There are 5 columns dealing with money: princp_paid, int_paid, fee_paid,
# recovs, and recovs_fee. princp_paid + int_paid + fee_paid is sometimes short
# of amt_paid. Be conservative and rewrite amt_paid to be sum of said 3.
# Also make all_cash_to_inv = amt_paid + recovs - recov_fees
# Fee paid is always positive, and by inspection it is money borrower pays out
pmt_hist[
    'amt_paid'] = pmt_hist['princp_paid'] + pmt_hist['int_paid'] + pmt_hist['fee_paid']
pmt_hist['recovs'].fillna(0, inplace=True)
pmt_hist['recov_fees'].fillna(0, inplace=True)
pmt_hist[
    'all_cash_to_inv'] = pmt_hist['amt_paid'] + pmt_hist['recovs'] - pmt_hist['recov_fees']

# turn all date columns into pandas timestamp _________________________________
month_dict = {
    'jan': '1-',
    'feb': '2-',
    'mar': '3-',
    'apr': '4-',
    'may': '5-',
    'jun': '6-',
    'jul': '7-',
    'aug': '8-',
    'sep': '9-',
    'oct': '10-',
    'nov': '11-',
    'dec': '12-'
}

# pmt_date ____________________________________________________________________
pmt_hist['pmt_date'] = pd.to_datetime(
    pmt_hist['pmt_date'].str[:3].str.lower().replace(month_dict) +
    pmt_hist['pmt_date'].str[3:],
    format='%m-%Y')

# date ________________________________________________________________________
pmt_hist['date'] = pd.to_datetime(
    pmt_hist['date'].str[:3].str.lower().replace(month_dict) +
    pmt_hist['date'].str[3:],
    format='%m-%Y')

# issue_d _____________________________________________________________________
pmt_hist['issue_d'] = pd.to_datetime(
    pmt_hist['issue_d'].str[:3].str.lower().replace(month_dict) +
    pmt_hist['issue_d'].str[3:],
    format='%m-%Y')

# first_credit_line ____________________________________________________________
pmt_hist['first_credit_line'] = pd.to_datetime(
    pmt_hist['first_credit_line'].str[:3].str.lower().replace(month_dict) +
    pmt_hist['first_credit_line'].str[3:],
    format='%m-%Y')

# status_period_end ____________________________________________________________
status_fix = {
    'Current': 'current',
    'Late (31-120 days)': 'late_120',
    'Fully Paid': 'paid',
    'Charged Off': 'charged_off',
    'Default': 'defaulted',
    'Late (16-30 days)': 'late_30',
    'In Grace Period': 'grace_15',
    'Issued': 'current'
}
pmt_hist['status_period_end'] = pmt_hist['status_period_end'].replace(
    status_fix)

# home_ownership _______________________________________________________________
home_ownership_fix = {
    'admin_us': 'other',
    'mortgage': 'mortgage',
    'rent': 'rent',
    'own': 'own',
    'other': 'other',
    'none': 'none',
    'any': 'none'
}
pmt_hist['home_ownership'] = pmt_hist['home_ownership'].str.lower().replace(
    home_ownership_fix)

# public_recs __________________________________________________________________
records_fix = {
    '*': 1
}  #leave nan as nan, but * had at least 1 from m_since_record
pmt_hist['public_recs'] = pmt_hist['public_recs'].replace(records_fix).astype(
    float)

# fico_apply __________________________________________________________________
fico_apply_fix = {'850': '850-850'}
pmt_hist['fico_apply'] = pmt_hist['fico_apply'].replace(fico_apply_fix)
pmt_hist['fico_apply'] = (pmt_hist['fico_apply'].str[:3].astype(int) +
                          pmt_hist['fico_apply'].str[4:].astype(int)) / 2
pmt_hist['fico_apply'] = pmt_hist['fico_apply'].astype(int)

# fico_last ___________________________________________________________________
fico_last_fix = {'845-HIGH': '845-849', 'LOW-499': '495-499'}
pmt_hist['fico_last'] = pmt_hist['fico_last'].replace(fico_last_fix)
pmt_hist.loc[pmt_hist['fico_last'] != 'MISSING', 'fico_last'] = (
    pmt_hist.loc[pmt_hist['fico_last'] != 'MISSING', 'fico_last'].str[:3]
    .astype(int) + pmt_hist.loc[pmt_hist['fico_last'] != 'MISSING',
                                'fico_last'].str[4:].astype(int)) / 2
pmt_hist.loc[pmt_hist['fico_last'] == 'MISSING', 'fico_last'] = pmt_hist.loc[
    pmt_hist['fico_last'] == 'MISSING', 'fico_apply']
pmt_hist['fico_last'] = pmt_hist['fico_last'].astype(int)

# revol_credit_bal ____________________________________________________________
pmt_hist['revol_credit_bal'] = pmt_hist['revol_credit_bal'].astype(
    float)

# fix on a few bad rows where I think there is a mistaken amt_paid ____________
pmt_hist.loc[(pmt_hist['pmt_date'].isnull() & pmt_hist['amt_paid'] > 0),
             'amt_paid'] = 0

# compress memory
changed_type_cols, pmt_hist = mg.reduce_memory(pmt_hist)


# map position to column
column_iloc_map = {
    col_name: pmt_hist.iloc[-1].index.get_loc(col_name)
    for col_name in pmt_hist.columns.values
}

# split into portions needing fixing and not needing fixing
dup_date_ids = pmt_hist[pmt_hist.duplicated(
    ['loan_id', 'date'])]['loan_id'].unique()
already_good = pmt_hist[~pmt_hist['loan_id'].isin(dup_date_ids)]
needs_fixing = pmt_hist[pmt_hist['loan_id'].isin(dup_date_ids)]
del pmt_hist

# fix dfs with duplicate dates
fixed_dfs = []
id_grouped = needs_fixing.groupby('loan_id')
for ids, group in tqdm(id_grouped):
    if ids in dup_date_ids:
        fixed_dfs.append(merge_dupe_dates(group))

# combine dfs
fixed_df = pd.concat(fixed_dfs)
pmt_hist = pd.concat([already_good, fixed_df])
del already_good, fixed_df

# want one entry for every month for every loan until "loan end".
# clean_pmt_history_2 ensured that there were not duplicate entries per month
# now we ensure that there's an entry for each month
id_grouped = pmt_hist.groupby('loan_id')

fixed_dfs = []
fixed_ids = []
for ids, group in tqdm(id_grouped):
    # Copy Paste finished below
    issue_d = group['issue_d'].min()
    first_date = group['date'].min()
    last_date = group['date'].max()
    expected_months = set(pd.DatetimeIndex(start=first_date, end=last_date, freq='MS'))
    actual_months = set(group['date'])
    to_make_months = list(expected_months.symmetric_difference(actual_months))
    to_make_months.sort()
    if len(to_make_months) > 1:
        months_to_copy = []
        for month in to_make_months:
            months_to_copy.append(
                find_closest_previous_record(
                    ids, issue_d, first_date, actual_months, month))
        copied = group[group['date'].isin(months_to_copy)].copy()
        copied['amt_paid'] = 0.0
        copied['date'] = to_make_months
        copied['amt_due'] = np.where(copied['date'] < first_date, 0, copied['amt_due'])
        fixed_dfs.append(pd.concat([group, copied]))
        fixed_ids.append(ids)
    else:
        pass

# combine the fixed entries with ones that don't need fixing
already_good = pmt_hist[~pmt_hist['loan_id'].isin(fixed_ids)]
fixed_df = pd.concat(fixed_dfs)
del pmt_hist
pmt_hist = pd.concat([already_good, fixed_df])
del already_good, fixed_df

# compress memory
changed_type_cols, pmt_hist = mg.reduce_memory(pmt_hist)

# resort to keep relevant rows together, reset index, save
pmt_hist.sort_values(by=['loan_id', 'date'], inplace=True)
pmt_hist.reset_index(inplace=True, drop=True)
pmt_hist.to_feather(os.path.join(config.data_dir, 'clean_pmt_history.fth'))
