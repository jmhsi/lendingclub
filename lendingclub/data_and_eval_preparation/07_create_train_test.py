'''
this makes the train and test sets as well as bootstrapped sets.
trainable loans are loans that are "done" enough
'''
import os
import pickle

import pandas as pd
# testing

from lendingclub import config, utils

dpath = config.data_dir
base_loan_info = pd.read_feather(os.path.join(dpath, 'base_loan_info.fth'))
eval_loan_info = pd.read_feather(os.path.join(dpath, 'eval_loan_info.fth'))
pmt_hist = pd.read_feather(os.path.join(dpath, 'scaled_pmt_hist.fth'))

def check_sample_distribution(df, sample, diff_thrsh=.05, check_cols=[], verbose=True):
    '''
    check if the distribution of the sample's col and df's col is sufficiently
    close. Default tolerance is 1% difference
    '''
    if not check_cols:
        check_cols = df.columns
    pop_n = len(df)
    s_n = len(sample)
    sample_miss = {}
    big_pct_diff = {}
    for col in check_cols:
        pop_group = df[col].value_counts(dropna=False)/pop_n
        s_group = sample[col].value_counts(dropna=False)/s_n
        temp_miss = {}
        temp_diff = {}
        for k in pop_group.keys():
            if k not in s_group.keys():
                if verbose:
                    print('{0} group for {2} column is missing entirely from the sample \
                      while population has {1}'.format(k, pop_group[k], col))
                temp_miss[k] = pop_group[k]
            else:
                pct_diff = abs(pop_group[k] - s_group[k])/pop_group[k]
                if pct_diff > diff_thrsh:
                    temp_diff[k] = pct_diff
        if temp_miss:
            sample_miss[col] = temp_miss
        if temp_diff:
            big_pct_diff[col] = temp_diff
    if sample_miss or big_pct_diff:
        print("There is a sampling concern")

def check_not_same_loans(tr, te):
    return bool(len(set(tr['id']).intersection(set(te['id']))) == 0)

def check_all_loans_accounted(tr, te, to):
    return bool(tr.shape[0] + te.shape[0] == to.shape[0])

def check_same_n_instances(df1, df2):
    return bool(df1.shape[0] == df2.shape[0])

def check_same_n_cols(df1, df2):
    return bool(df1.shape[1] == df2.shape[1])

def check_train_test_testable(train, test, testable, train1, test1, testable1):
    '''
    First set for loan_info, second set for eval_loan_info
    '''
    print(train.shape, test.shape, testable.shape, train1.shape, test1.shape, testable1.shape)
    assert check_not_same_loans(train, test)
    assert check_all_loans_accounted(train, test, testable)
    assert check_not_same_loans(train1, test1)
    assert check_all_loans_accounted(train1, test1, testable1)
    assert check_same_n_instances(train, train1)
    assert check_same_n_instances(test, test1)
    assert check_same_n_instances(testable, testable1)
    assert check_same_n_cols(train, test)
    assert check_same_n_cols(train1, test1)
    return True

#from 2010-1-1 onward, take out min(10%, 2000) loans to set aside as train
doneness = .95
train_testable_eval_loan_info = eval_loan_info.query('maturity_time_stat_adj >= @doneness or maturity_paid_stat_adj >= @doneness')
train_testable_ids = train_testable_eval_loan_info['id']
train_testable_loan_info = base_loan_info.query('id in @train_testable_ids')

assert train_testable_eval_loan_info.shape[0] == train_testable_loan_info.shape[0]

# # save loans useable for training and testing
# train_testable_eval_loan_info.reset_index(drop=True).to_feather(os.path.join(dpath, 'train_testable_eval_loan_info.fth'))
# train_testable_loan_info.reset_index(drop=True).to_feather(os.path.join(dpath, 'train_testable_base_loan_info.fth'))



issue_d_g = train_testable_eval_loan_info.groupby('issue_d')
test_ids = []
check_cols = ['target_strict', 'grade']
for date, group in issue_d_g:
    if date >= pd.to_datetime('2010-1-1'):
        print('sampling {0} for issue_d group {1}'.format(min(int(len(group)*.1), 2000), date))
        samp = group.sample(n=min(int(len(group)*.1), 2000), random_state=42)
        if check_sample_distribution(group, samp, check_cols=check_cols, verbose=False):
            print()
        test_ids.extend(samp['id'].tolist())

test_eval_loan_info = train_testable_eval_loan_info.query('id in @test_ids')
test_loan_info = train_testable_loan_info.query('id in @test_ids')

train_eval_loan_info = train_testable_eval_loan_info.query('id not in @test_ids')
train_loan_info = train_testable_loan_info.query('id not in @test_ids')

if check_train_test_testable(train_eval_loan_info, test_eval_loan_info, train_testable_eval_loan_info,
                             train_loan_info, test_loan_info, train_testable_loan_info):
    # save
#     test_eval_loan_info.reset_index(drop=True).to_feather(os.path.join(dpath, 'test_eval_loan_info.fth'))
#     test_loan_info.reset_index(drop=True).to_feather(os.path.join(dpath, 'test_base_loan_info.fth'))
#     train_eval_loan_info.reset_index(drop=True).to_feather(os.path.join(dpath, 'train_eval_loan_info.fth'))
#     train_loan_info.reset_index(drop=True).to_feather(os.path.join(dpath, 'train_base_loan_info.fth'))
    train_test_ids_dict = {}
    train_test_ids_dict['train_testable'] = train_testable_ids.tolist()
    train_test_ids_dict['train'] = train_loan_info['id'].tolist()
    train_test_ids_dict['test'] = test_loan_info['id'].tolist()
    with open(os.path.join(dpath, 'train_test_ids.pkl'), 'wb') as file:
        pickle.dump(train_test_ids_dict, file)
    

    # make 10 bootstrap month-by-month test_loan_infos (and maybe test_eval_loan_infos?)
    bootstrap_sample_ids = {}
    issue_d_g = test_eval_loan_info.groupby('issue_d')
    for i in range(10):
        to_concat = []
        for d, g in issue_d_g:
            to_concat.append(g.sample(len(g), replace=True))
        df = pd.concat(to_concat)
#         df.reset_index(drop=True).to_feather(os.path.join(dpath, 'test_eval_loan_info_{0}_bootstrap.fth'.format(i)))
        bootstrap_sample_ids[i] = df['id'].tolist()
    
    with open(os.path.join(dpath, 'bootstrap_test_ids.pkl'), 'wb') as file:
        pickle.dump(bootstrap_sample_ids, file)
