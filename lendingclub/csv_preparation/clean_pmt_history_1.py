from tqdm import tqdm
import os
import sys
import pandas as pd
from lendingclub import config
import j_utils.munging as mg

csv_path = config.wrk_csv_dir
# for now its always been one csv. Will have to revisit if they break it out to multiple
pmt_hist_fnames = [f for f in os.listdir(csv_path) if 'PMTHIST' in f]
pmt_hist_path = os.path.join(csv_path, pmt_hist_fnames[0])
pmt_hist = pd.read_csv(pmt_hist_path, low_memory=False)
print("{:,}".format(len(pmt_hist)) + " rows of pmt_hist loaded")

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
pmt_hist.ix[pmt_hist['fico_last'] != 'MISSING', 'fico_last'] = (
    pmt_hist.ix[pmt_hist['fico_last'] != 'MISSING', 'fico_last'].str[:3]
    .astype(int) + pmt_hist.ix[pmt_hist['fico_last'] != 'MISSING',
                               'fico_last'].str[4:].astype(int)) / 2
pmt_hist.ix[pmt_hist['fico_last'] == 'MISSING', 'fico_last'] = pmt_hist.ix[
    pmt_hist['fico_last'] == 'MISSING', 'fico_apply']
pmt_hist['fico_last'] = pmt_hist['fico_last'].astype(int)

# revol_credit_bal ____________________________________________________________
pmt_hist['revol_credit_bal'] = pmt_hist['revol_credit_bal'].astype(
    float)

# fix on a few bad rows where I think there is a mistaken amt_paid ____________
pmt_hist.ix[(pmt_hist['pmt_date'].isnull() & pmt_hist['amt_paid'] > 0),
            'amt_paid'] = 0

# compress memory
changed_type_cols, pmt_hist = mg.reduce_memory(pmt_hist)

# save
dpath = config.data_dir
pmt_hist.to_feather(os.path.join(dpath, 'clean_pmt_history_1.fth'))

