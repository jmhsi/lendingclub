'''
Reads in payment history, does lots of cleaning
'''
import os
import pickle
import sys

import pandas as pd
from tqdm import tqdm

import j_utils.munging as mg
from lendingclub import config
import lendingclub.csv_preparation.clean_pmt_history as cph


if __name__ == '__main__':
    # LOADING
    csv_path = config.wrk_csv_dir
    # for now its always been one csv. Will have to revisit if they break it out to multiple
    pmt_hist_fnames = [f for f in os.listdir(csv_path) if 'PMTHIST' in f]
    if len(pmt_hist_fnames) > 1:
        sys.exit('more than one payment history file, need to change this code')

    # load in dev_ids.pkl, pmt_hist_skiprows, dtypes
    with open(os.path.join(config.data_dir, 'dev_ids.pkl'), "rb") as f:
        dev_ids = pickle.load(f)
    with open(os.path.join(config.data_dir, 'pmt_hist_skiprows.pkl'), "rb") as f:
        pmt_hist_skiprows = pickle.load(f)
    with open(os.path.join(config.data_dir, 'pmt_hist_dtypes.pkl'), 'rb') as f:
        dtypes = pickle.load(f)
        
    print('loading pmt_hist; skipping {0} rows'.format(len(pmt_hist_skiprows)))
    pmt_hist = pd.read_csv(os.path.join(csv_path, pmt_hist_fnames[0]),
                           skiprows=pmt_hist_skiprows,
                           na_values=['*'],
                           dtype=dtypes)
    print("{:,}".format(len(pmt_hist)) + " rows of pmt_hist loaded")


    
    # COMPRESS MEMORY
    changed_type_cols, pmt_hist = mg.reduce_memory(pmt_hist)
    
    # DATA INTEGRITY PART 1
    id_grouped = pmt_hist.groupby('LOAN_ID')
    strange_pmt_hist_ids = []
    for ids, group in tqdm(id_grouped):
        if cph.detect_strange_pmt_hist(group):
            strange_pmt_hist_ids.append(ids)
    with open(os.path.join(config.data_dir, 'strange_pmt_hist_ids.pkl'), "wb") as f:
        pickle.dump(strange_pmt_hist_ids, f)
    
    # DATA PROCESSING
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

#     # There is a problem with the inquiries 6m column. Some are nan values and some
#     # are marked '*' with no explanation. inq6m should be in loan info so dropping
#     pmt_hist.drop('inq_6m', axis=1, inplace=True)

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
    for col in ['pmt_date', 'date', 'issue_d', 'first_credit_line']:
        cph.pmt_hist_fmt_date(pmt_hist, col)


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

    # fix dfs with duplicate dates to be one per month
    fixed_dfs = []
    id_grouped = needs_fixing.groupby('loan_id')
    for ids, group in tqdm(id_grouped):
        if ids in dup_date_ids:
            fixed_dfs.append(cph.merge_dupe_dates(group, column_iloc_map))

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
        fix_df = cph.insert_missing_dates(group, ids)
        if fix_df is not None:
            fixed_dfs.append(fix_df)
            fixed_ids.append(ids)

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
    
    
