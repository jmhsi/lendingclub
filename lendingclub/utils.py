'''
utility functions for loading
'''
import os
import pickle
import pandas as pd
from lendingclub import config

def cut_to_ids(df, ids):
    '''
    cuts a dataframe to a list of ids
    '''
    query = 'id in @ids'
    return df.query(query)


def load_dataset(ds_type = 'train'):
    '''
    load in train or test datasets (base_loan_info, eval_loan_info, ids)
    '''
    with open(os.path.join(config.data_dir, 'train_test_ids.pkl'), 'rb') as file:
        train_test_ids_dict = pickle.load(file)
    base_loan_info = pd.read_feather(os.path.join(config.data_dir, 'base_loan_info.fth'))
    eval_loan_info = pd.read_feather(os.path.join(config.data_dir, 'eval_loan_info.fth'))
        
    if ds_type not in ['train', 'test', 'train_testable']:
        print('ds_type must be "train", "test", or "train_testable"')
        return None
    if ds_type == 'test':
        ids = train_test_ids_dict['test']
    elif ds_type == 'train':
        ids = train_test_ids_dict['train']
    else:
        ids = train_test_ids_dict['train_testable']

    return cut_to_ids(base_loan_info, ids), cut_to_ids(eval_loan_info, ids), ids
