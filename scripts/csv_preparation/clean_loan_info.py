
'''
maturity time and maturity paid are floats from 0 to 1 that express how "done"
a loan is either time-wise, or money wise. There are loan-status adjusted versions as well.
I use these because I want to include as much data for my models as possible while recognizing that
there is uncertainty in knowing whether a loan was good or bad if it is ongoing.

For example, if a loan is 120 days late, we know that loan is likely a very bad investment that our model should not be choosing. Is it possible that the loan all of a sudden becomes current and you get a massive return due to accumulated late fees? Yes, but not likely. In any case, I would rather incorporate that likely-to-be-bad loan into the model now instead of wait 2-ish months for that loan to truly go through the charged-off process.

maturity_time is how close to original maturity the loan is, regardless of how much the loan has paid back and/or followed the expected payment schedule.
maturity_paid is how close the loan is to completing all its payments (
total_payments_received/(total_expected_payments at point in time, with adjustments for lateness))

status adjusted are adjusting the maturity calculations knowing that if the loan does go the charge-off route, it has x months left or will recover .1 percent of remaining outstanding principal on avg.

Some examples of loans:
1) A loan is issued last month and almost pays off all the outstanding principal this month (maybe a borrower found better loan terms elsewhere, and took out that new loan to almost completely pay down the ) would have maturity_time near 0 and maturity_paid near 1
2) A 3 year loan that is 8 months in and is 120 days late has a low maturity_time and fairly high maturity_paid, as there is an adjustment for denominator (aside form what was already paid to date by the loan, only expecting a 10% recovery on remaining outstanding principal)
'''

import sys
import os
import pandas as pd
import math
import re
from tqdm import tqdm_notebook, tqdm
sys.path.append(os.path.join(os.path.expanduser('~'), 'projects'))
sys.path.append(os.path.join(os.path.expanduser('~'), 'projects', 'lendingclub', 'scripts', 'csv_preparation'))
import j_utils.munging as mg
import rem_to_be_paid as rtbp

# load data, turn python Nones into np.nans
dpath = os.path.join(os.path.expanduser('~'), 'projects', 'lendingclub', 'data')
loan_info = pd.read_feather(os.path.join(dpath, 'raw_loan_info.fth'))
loan_info.fillna(value=pd.np.nan, inplace=True)

#turn all date columns into pandas timestamp ________________________________
month_dict = {
    'jan': '1',
    'feb': '2',
    'mar': '3',
    'apr': '4',
    'may': '5',
    'jun': '6',
    'jul': '7',
    'aug': '8',
    'sep': '9',
    'oct': '10',
    'nov': '11',
    'dec': '12'
}
# date cols
date_cols = [
    'issue_d', 'earliest_cr_line', 'last_pymnt_d', 'last_credit_pull_d',
    'next_pymnt_d', 'sec_app_earliest_cr_line', 'hardship_start_date',
    'hardship_end_date', 'payment_plan_start_date', 'debt_settlement_flag_date',
    'settlement_date',
]
for col in date_cols:
    loan_info[col] = loan_info[col].str.strip()
    loan_info[col] = loan_info[col].str.lower()
    loan_info[col] = pd.to_datetime(
        loan_info[col].str[:3].str.lower().replace(month_dict) +
        loan_info[col].str[3:],
        format='%m-%Y')
    
# Cleanups ___________________________________________________________________
# int_rate
loan_info['int_rate'] = loan_info['int_rate'] / 100
# installment funded 
rename_dict = {'installment': 'installment_currently'}
loan_info.rename(rename_dict, inplace=True, axis=1)
# emp_title
loan_info['emp_title'] = loan_info['emp_title'].str.lower()
# home_ownership
dic_home_ownership = {
    'mortgage': 'mortgage',
    'rent': 'rent',
    'own': 'own',
    'other': 'other',
    'none': 'none',
    'any': 'none'
}
loan_info['home_ownership'] = loan_info['home_ownership'].str.lower().replace(
    dic_home_ownership)
# verification_status and verification_status_joint
dic_verification_status = {
    'VERIFIED - income': 'platform',
    'VERIFIED - income source': 'source',
    'not verified': 'none',
    'Source Verified': 'source',
    'Not Verified': 'none',
    'Verified': 'platform'
}
loan_info['verification_status'] = loan_info['verification_status'].replace(
    dic_verification_status)
loan_info['verification_status_joint'] = loan_info[
    'verification_status_joint'].replace(dic_verification_status)
# status
dic_status = {
    'Current': 'current',
    'Charged Off': 'charged_off',
    'Fully Paid': 'paid',
    'Late (31-120 days)': 'late_120',
    'In Grace Period': 'grace_15',
    'Late (16-30 days)': 'late_30',
    'Default': 'defaulted',
    'Issued': 'current'
}
loan_info['loan_status'] = loan_info['loan_status'].apply(
    lambda x: re.sub('Does not meet the credit policy.  Status:', '', x))
loan_info['loan_status'] = loan_info['loan_status'].apply(
    lambda x: re.sub('Does not meet the credit policy. Status:', '', x))
loan_info['loan_status'] = loan_info['loan_status'].replace(dic_status)
loan_info['hardship_loan_status'] = loan_info['hardship_loan_status'].replace(dic_status)
#title
loan_info['title'] = loan_info['title'].str.lower()
#application_type
loan_info['application_type'] = loan_info['application_type'].str.lower()
#revol_util
loan_info['revol_util'] = loan_info['revol_util'].apply(
    lambda x: float(x.strip('%')) / 100 if pd.notnull(x) else np.nan)
#all_util
loan_info['all_util'] = loan_info['all_util'] / 100.
# pct_tl_nvr_dlq
loan_info['pct_tl_nvr_dlq'] = loan_info['pct_tl_nvr_dlq'] / 100.
# percent_bc_gt_75
loan_info['percent_bc_gt_75'] = loan_info['percent_bc_gt_75'] / 100.
# dti
loan_info['dti'] = loan_info['dti'] / 100.
# dti_joint
loan_info['dti_joint'] = loan_info['dti_joint'] / 100.
# il_util
loan_info['il_util'] = loan_info['il_util'] / 100.
# bc_util
loan_info['bc_util'] = loan_info['bc_util'] / 100.
# sec_app_revol_util
loan_info['sec_app_revol_util'] = loan_info['sec_app_revol_util'] / 100.
# settlement_percentage
loan_info['settlement_percentage'] = loan_info['settlement_percentage'] / 100.

# check that percents are between 0 and 1, not 0 and 100
pct_cols = []
for col in loan_info.columns:
    if any(x in col for x in ['pct', 'percent', 'util', 'dti', 'rate']):
        pct_cols.append(col)
        
for col in pct_cols:
    if loan_info[col].mean() > 1:
        print('this col needs to be turned into a decimal form of percent: ',col)
    if loan_info[col].median() > 1:
        print('this col needs to be turned into a decimal form of percent: ',col)
        
# Adding columns of interest _________________________________________________        
# unreceived principal, not overwriting out_prncp
loan_info['unreceived_prncp'] = loan_info['funded_amnt'] - loan_info['total_rec_prncp']
loan_info['unreceived_prncp'] = np.where(loan_info['unreceived_prncp'] <= 0.019, 0, loan_info['unreceived_prncp'])
loan_info['unreceived_prncp'] = loan_info['unreceived_prncp'].round(2)

# want to calculate what installment originally was
loan_info['installment_at_funded'] = np.pmt(loan_info['int_rate']/12, loan_info['term'], -loan_info['funded_amnt'])

# have a max_date for reference in making end_d
max_date = loan_info['last_pymnt_d'].max()

# end_d to me means the date we can stop tracking things about the loan. Should be defunct
def applyEndD(status, group):
    if status == 'charged_off':
        #split the group into two groups, one which has paid something, and other which has paid nothing
        never_paid = group[group['last_pymnt_d'].isnull()]
        has_paid = group[group['last_pymnt_d'].notnull()]

        # 4 months of late (1-120) and then 1 month of chargeoff, so 5 months
        never_paid['end_d'] = never_paid['issue_d'] + pd.DateOffset(months=+5)
        has_paid['end_d'] = has_paid['last_pymnt_d'] + pd.DateOffset(months=+5)

        group.ix[never_paid.index.values, 'end_d'] = never_paid['end_d']
        group.ix[has_paid.index.values, 'end_d'] = has_paid['end_d']
        return group['end_d']
    elif status == 'paid':
        return group['last_pymnt_d']
    else:
        return pd.Series([max_date] * len(group), index=group.index.values)
    
# make end_d
status_grouped = loan_info.groupby('loan_status')
end_d_series = pd.Series([])
for status, group in status_grouped:
    end_d_series = end_d_series.append(
        applyEndD(status, group), verify_integrity=True)
loan_info['end_d'] = end_d_series
loan_info.loc[loan_info['end_d'] > max_date, 'end_d'] = max_date

# adding line_history in days, months, and years using pandas .dt functions
loan_info['line_history_d'] = (loan_info['issue_d'] - loan_info['earliest_cr_line']).dt.days
loan_info['line_history_m'] = (loan_info['issue_d'].dt.year - loan_info['earliest_cr_line'].dt.year)*12 + (loan_info['issue_d'].dt.month - loan_info['earliest_cr_line'].dt.month)
loan_info['line_history_y'] = (loan_info['issue_d'].dt.year - loan_info['earliest_cr_line'].dt.year) + (loan_info['issue_d'].dt.month - loan_info['earliest_cr_line'].dt.month)/12
#credit_score
loan_info['fico'] = (
    loan_info['fico_range_high'] + loan_info['fico_range_low']) / 2

# maturity_time
loan_info['months_passed'] = ((
    max_date - loan_info['issue_d']).dt.days *
                            (12 / 365.25)).round()
loan_info['maturity_time'] = loan_info['months_passed'] / loan_info['term']
loan_info['maturity_time'] = np.where(loan_info['maturity_time'] >= 1, 1,
                                      loan_info['maturity_time'])

# make rem_to_be_paid
loan_info['rem_to_be_paid'] = rtbp.apply_rem_to_be_paid(
    loan_info['unreceived_prncp'].values, loan_info['installment_currently'].values,
    loan_info['int_rate'].values)

loan_info['maturity_paid'] = loan_info['total_pymnt'] / (
    loan_info['total_pymnt'] + loan_info['rem_to_be_paid'])

# making status adjusted versions of mat_time, mat_paid
# grace = 35%, late_30 = 64%, late_120 = 98%, 
# See https://www.lendingclub.com/info/demand-and-credit-profile.action for %s used
# maturity_time_stat_adj = 
# maturity_time * prob_not_def + months_passed/months_to_default * prob_def
loan_info['maturity_time_stat_adj'] = np.where(loan_info['loan_status'] == 'grace_15', loan_info['maturity_time']*(1-.35) + ((loan_info['months_passed']/(loan_info['months_passed'] + 4))*.35), 
        np.where(loan_info['loan_status'] == 'late_30', loan_info['maturity_time']*(1-.64) + ((loan_info['months_passed']/(loan_info['months_passed'] + 3))*.64), 
        np.where(loan_info['loan_status'] == 'late_120', loan_info['maturity_time']*(1-.98) + ((loan_info['months_passed']/(loan_info['months_passed'] + 1))*.98), loan_info['maturity_time']
        )))
loan_info['maturity_time_stat_adj'] = np.minimum(1, loan_info['maturity_time_stat_adj'])

# maturity_paid_stat_adj = 
# maturity_paid * prob_not_def + total_paid/total_paid_and_outstanding * prob_def
# .1 is from assuming 10% recovery on defaulted/charged_off loans
loan_info['maturity_paid_stat_adj'] = np.where(loan_info['loan_status'] == 'grace_15', loan_info['maturity_paid']*(1-.35) + ((loan_info['total_pymnt']/(loan_info['total_pymnt'] + .1*loan_info['unreceived_prncp']))*.35), 
        np.where(loan_info['loan_status'] == 'late_30', loan_info['maturity_paid']*(1-.64) + ((loan_info['total_pymnt']/(loan_info['total_pymnt'] + .1*loan_info['unreceived_prncp']))*.64), 
        np.where(loan_info['loan_status'] == 'late_120', loan_info['maturity_paid']*(1-.98) + ((loan_info['total_pymnt']/(loan_info['total_pymnt'] + .1*loan_info['unreceived_prncp']))*.98), loan_info['maturity_paid']
        )))
loan_info['maturity_paid_stat_adj'] = np.minimum(1, loan_info['maturity_paid_stat_adj'])

# final adjustments to status_adj based on done statuses
loan_info.loc[loan_info['loan_status'].isin(['paid', 'charged_off', 'defaulted']),'maturity_paid_stat_adj'] = 1
loan_info.loc[loan_info['loan_status'].isin(['paid', 'charged_off', 'defaulted']),'maturity_time_stat_adj'] = 1

# target_loose
loan_info['target_loose'] = np.where(loan_info['loan_status'].isin(['charged_off', 'defaulted']), 1, 0)

# pull out long string columns
str_cols = loan_info.select_dtypes('object').columns
strip_cols = ['desc', 'emp_title', 'title', 'url']
strings_df = loan_info[strip_cols]
loan_info.drop(columns=strip_cols, inplace=True)
strings_df['id'] = loan_info['id']

# make target strict, anything that was ever late is marked "bad"
bad_statuses = set(['late_120', 'defaulted', 'charged_off', 'late_30'])
pmt_hist = pd.read_feather(os.path.join(dpath, 'clean_pmt_history_3.fth'))
target_strict_dict = {}
id_grouped = pmt_hist.groupby('loan_id')
for ids, group in tqdm(id_grouped):
    statuses = set(group['status_period_end'])
    if len(statuses.intersection(bad_statuses)) > 0:
        target_strict_dict[ids] = 1
    else:
        target_strict_dict[ids] = 0
target_strict = pd.DataFrame.from_dict(target_strict_dict, orient='index').reset_index(drop=False)
target_strict.columns = ['id', 'target_strict']
loan_info.rename({'loan_id': 'id'}, axis=1, inplace=True)
loan_info = pd.merge(loan_info, target_strict, how='outer', on='id')

# add orig_amt_due and roi_simple
loan_info['orig_amt_due'] = loan_info['term'] * loan_info['installment_amount']
loan_info['roi_simple'] = loan_info['total_pymnt']/loan_info['funded_amnt']

# More Data Cleanup __________________________________________________________
# home_ownership: none should be other
loan_info['home_ownership'].replace({'none': 'other'}, inplace=True)
# annual_income has 4 nulls. Just fill with 0
loan_info['annual_inc'].replace({np.nan: 0.0}, inplace=True)
# drop the one null zip_code
loan_info = loan_info[loan_info['zip_code'].notnull()]
# drop the loans where earliest_cr_line is null
loan_info = loan_info[loan_info['earliest_cr_line'].notnull()]
# drop null chargeoff_within_12_mths
loan_info = loan_info[loan_info['chargeoff_within_12_mths'].notnull()]
# drop null tax_liens
loan_info = loan_info[loan_info['tax_liens'].notnull()]
# drop loans that have this null
loan_info = loan_info[loan_info['inq_last_6mths'].notnull()]

# Drop columns _______________________________________________________________
# Dropping these since I don't want them and they might confuse me.
# There is no reason why I care about money that went just to investors rather
# than to lending club as well when they top off loans.
loan_info.drop(['funded_amnt_inv',
                'out_prncp_inv'], axis = 1, inplace = True)

# last cleanups before storing
loan_info.fillna(value=np.nan, inplace=True)
strings_df.fillna(value=np.nan, inplace=True)

# reduce memory and store
_, strings_df = mg.reduce_memory(strings_df)
strings_df.reset_index(drop=True, inplace=True)
_, loan_info = mg.reduce_memory(loan_info)
loan_info.reset_index(drop=True, inplace=True)
strings_df.to_feather(os.path.join(dpath, 'strings_loan_info_df.fth'))
loan_info.to_feather(os.path.join(dpath, 'loan_info.fth'))
