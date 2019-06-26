from tqdm import tqdm_notebook, tqdm
import os
import pandas as pd

def find_dupe_dates(group):
    return pd.to_datetime(group[group.duplicated('date')]['date'].values)

def merge_dupe_dates(group):
    df_chunks = []
    
    dupe_dates = find_dupe_dates(group)
    df_chunks.append(group[~group['date'].isin(dupe_dates)])
    
    for date in dupe_dates:
        problem_rows = group[group['date'] == date]
        ori_index = problem_rows.index
        keep_row = problem_rows.iloc[-1].to_dict()
        keep_row['outs_princp_beg'] = problem_rows.ix[ori_index[0],column_iloc_map['outs_princp_beg']]
        
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

# load data
dpath = os.path.join(os.path.expanduser('~'), 'projects', 'lendingclub', 'data')
pmt_hist = pd.read_feather(os.path.join(dpath, 'clean_pmt_history_1.fth'))

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

# resort to keep relevant rows together, reset index, save
pmt_hist.sort_values(by=['loan_id', 'date'], inplace=True)
pmt_hist.reset_index(inplace=True, drop=True)
pmt_hist.to_feather(os.path.join(dpath, 'clean_pmt_history_2.fth'))
