from tqdm import tqdm_notebook, tqdm
import os
import pandas as pd
import numpy as np

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
    else:
        find_closest_previous_record(ids, issue_d, first_date, actual_months, prev_month)
        
# load data
dpath = os.path.join(os.path.expanduser('~'), 'projects', 'lendingclub', 'data')
pmt_hist = pd.read_feather(os.path.join(dpath, 'clean_pmt_history_2.fth'))

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
                months_to_copy.append(find_closest_previous_record(ids, issue_d, first_date, actual_months, month))
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

# resort to keep relevant rows together, reset index, save
pmt_hist.sort_values(by=['loan_id', 'date'], inplace=True)
pmt_hist.reset_index(inplace=True, drop=True)
pmt_hist.to_feather(os.path.join(dpath, 'clean_pmt_history_3.fth'))
