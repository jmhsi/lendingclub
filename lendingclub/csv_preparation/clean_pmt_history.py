import numpy as np
import pandas as pd

def find_dupe_dates(group):
    '''finds duplicated dates in groupby group'''
    return pd.to_datetime(group[group.duplicated('date')]['date'].values)

def merge_dupe_dates(group, column_iloc_map):
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
        keep_row['outs_princp_beg'] = problem_rows.iloc[0,column_iloc_map['outs_princp_beg']]
        summed = problem_rows.sum()
        keep_row['princp_paid'] = summed['princp_paid']
        keep_row['int_paid'] = summed['int_paid']
        keep_row['fee_paid'] = summed['fee_paid']
        # keep_row['amt_due'] = summed['amt_due']
        keep_row['amt_paid'] = summed['amt_paid']
        keep_row['charged_off_this_month'] = summed['charged_off_this_month']
        keep_row['charged_off_amt'] = summed['charged_off_amt']
        keep_row['recovs'] = summed['recovs']
        keep_row['recov_fees'] = summed['recov_fees']
        keep_row['all_cash_to_inv'] = summed['all_cash_to_inv']
        to_append = pd.DataFrame(keep_row, index=[ori_index[-1]])
        df_chunks.append(to_append)
    return pd.concat(df_chunks)

def insert_missing_dates(group, ids, verbose = False):
    '''
    redoes date so that there is one entry for each date
    '''
    # Copy Paste finished below
    issue_d = group['issue_d'].min()
    first_date = group['date'].min()
    last_date = group['date'].max()
    expected_months = set(pd.date_range(start=first_date, end=last_date, freq='MS'))
    actual_months = set(group['date'])
    to_make_months = list(expected_months.symmetric_difference(actual_months))
    to_make_months.sort()
    if len(to_make_months) > 0:
        months_to_copy = []
        for month in to_make_months:
            months_to_copy.append(
                find_closest_previous_record(
                    ids, issue_d, first_date, actual_months, month))
        copied = group[group['date'].isin(months_to_copy)].copy()
        copied['amt_paid'] = 0.0
        copied['date'] = to_make_months
        copied['amt_due'] = np.where(copied['date'] < first_date, 0, copied['amt_due'])
        return pd.concat([group, copied])
    else:
        if verbose:
            print('somehow there were no dates to add? id: {0}'.format(ids))
        return None


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

def detect_strange_pmt_hist(group, verbose=False):
    '''
    for each group in pmt_hist.groupby('LOAN_ID'), check that the 
    original due_amt is close to what is expected based on term, rate
    '''
    first_idx = group.index[0]
    exp_pmt = np.pmt(group.at[first_idx,'InterestRate']/12., group.at[first_idx,'term'], -group.at[first_idx,'PBAL_BEG_PERIOD'])
    rep_pmt = group.at[first_idx,'MONTHLYCONTRACTAMT']
    if verbose:
        print('expected pmt: {0}, reported pmt: {1}'.format(exp_pmt, rep_pmt))
    if abs(exp_pmt - rep_pmt)/(exp_pmt) > .01:
        return True
    return False

def pmt_hist_fmt_date(df, col):
    '''
    Specifically reformats pmt_hist dates in the expected way
    '''
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

    df[col] = pd.to_datetime(
        df[col].str[:3].str.lower().replace(month_dict) +
        df[col].str[3:],
        format='%m-%Y')
