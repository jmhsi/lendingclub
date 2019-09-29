import time
import os
import sys
import pandas as pd
from lendingclub import config
import j_utils.munging as mg

# Get the loan_info csvs to iterate over ______________________________________
files = os.listdir(config.wrk_csv_dir)
print("merging the separate loan info csvs")
loan_info_files = [
    file_ for file_ in files
    if not (file_.startswith('.') | file_.startswith('lc_') |
            file_.startswith('PMTHIST') | file_.startswith('LCData'))
]

to_concat = []
for file_ in loan_info_files:
    print('loading in {0}'.format(file_))
    to_concat.append(
        pd.read_csv(os.path.join(config.wrk_csv_dir, file_),
                    header=1,
                    engine='python',
                    skipfooter=2))

loan_info = pd.concat(to_concat)

# Block to ensure that rows that aren't actually loans are dropped ____________
# All loans must have int/term/funded
loan_info = loan_info[loan_info['term'].notnull()]
loan_info['int_rate'] = loan_info['int_rate'].str.strip('%').astype(float)
loan_info['term'] = loan_info['term'].str[:3].astype(int)
loan_info = loan_info[(loan_info['int_rate'] > 0) & (loan_info['term'] > 0) &
                      (loan_info['funded_amnt'] > 0)]

# compress memory
changed_type_cols, loan_info = mg.reduce_memory(loan_info)

# Reset index and set id to int______________________
loan_info.reset_index(drop=True, inplace=True)
loan_info['id'] = loan_info['id'].astype(int)

# trying out feather data format
fname = 'raw_loan_info.fth'
loan_info.to_feather(os.path.join(config.data_dir, fname))
