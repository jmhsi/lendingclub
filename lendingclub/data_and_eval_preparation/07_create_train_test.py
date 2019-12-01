'''
this makes the train and test sets as well as bootstrapped sets.
trainable loans are loans that are "done" enough
'''
import os
import pickle

import pandas as pd
# testing
from lendingclub import config, utils
from lendingclub.data_and_eval_preparation import create_train_test as ctt
from sklearn.model_selection import train_test_split

dpath = config.data_dir
base_loan_info = pd.read_feather(os.path.join(dpath, 'base_loan_info.fth'))
eval_loan_info = pd.read_feather(os.path.join(dpath, 'eval_loan_info.fth'))
print(base_loan_info.shape, eval_loan_info.shape)

with open(os.path.join(config.data_dir, 'strange_pmt_hist_ids.pkl'), 'rb') as f:
    strange_pmt_hist_ids = pickle.load(f)
    
print('dropping {0} strange loans based on strange_pmt_hist_ids.pkl'.format(len(strange_pmt_hist_ids)))
base_loan_info = base_loan_info.query('id not in @strange_pmt_hist_ids')
eval_loan_info = eval_loan_info.query('id not in @strange_pmt_hist_ids')
print(base_loan_info.shape, eval_loan_info.shape)

#from 2010-1-1 onward, take out min(10%, 2000) loans to set aside as test
doneness = .95
train_testable_eval_loan_info = eval_loan_info.query('maturity_time_stat_adj >= @doneness or maturity_paid_stat_adj >= @doneness')
train_testable_ids = train_testable_eval_loan_info['id']
X_train, X_test, _, _ = train_test_split(train_testable_eval_loan_info, train_testable_eval_loan_info['target_strict'].values, stratify=train_testable_eval_loan_info['grade'], test_size=0.1)
# remove loans before 2010-1-1 from test and add them to train
add_to_train = X_test.query('issue_d < "2010-1-1"')
X_train = pd.concat([X_train, add_to_train])
train_ids = X_train['id'].tolist()
X_test = X_test.query('id not in @train_ids')
test_ids = X_test['id'].tolist()
assert len(set(train_ids).intersection(test_ids)) == 0

train_test_ids_dict = {}
train_test_ids_dict['train_testable'] = train_testable_ids.tolist()
train_test_ids_dict['train'] = train_ids
train_test_ids_dict['test'] = test_ids

# make 10 bootstrap month-by-month test_loan_infos (and maybe test_eval_loan_infos?)
bootstrap_sample_idx = {}
issue_d_g = X_test.groupby('issue_d')
for i in range(10):
    to_concat = []
    for d, g in issue_d_g:
        to_concat.append(g.sample(len(g), replace=True))
    df = pd.concat(to_concat)
    bootstrap_sample_idx[i] = df.index.tolist()
    
# save
with open(os.path.join(dpath, 'train_test_ids.pkl'), 'wb') as file:
    pickle.dump(train_test_ids_dict, file)    
with open(os.path.join(dpath, 'bootstrap_test_idx.pkl'), 'wb') as file:
    pickle.dump(bootstrap_sample_idx, file)
