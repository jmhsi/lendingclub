import os
import pickle
import json
import sys
from typing import List
import argparse

import numpy as np
import pandas as pd
import seaborn as sns
# testing
from pandas.testing import assert_frame_equal
from tqdm import tqdm

import j_utils.munging as mg
from lendingclub import config, utils
from lendingclub.lc_utils import gen_datasets

parser = argparse.ArgumentParser()
parser.add_argument('--model', '-m', help='specify model(s) to train')

if not len(sys.argv) > 1:
    model_n = 'baseline' # , 'A', 'B', 'C', 'D', 'E', 'F', 'G'

def get_topn_ret(model, eval_df, n, return_col='0.07'): #, bootstrap=False
    '''
    Picks loans and get returns based on maximizing model_score
    '''
    assert n <= 1
    assert n >= 0
#     if bootstrap:
#         eval_df = eval_df.sample(frac=1, replace=True)
    return eval_df.nlargest(int(round(len(eval_df)*n)), f'{model}_score')['0.07'].mean()

def get_topn_def_pct(model, eval_df, n): #, bootstrap=False
    '''
    get the def percents with the top_n
    '''
    assert n <= 1
    assert n >= 0
#     if bootstrap:
#         eval_df = eval_df.sample(frac=1, replace=True)
    n_pick = int(round(len(eval_df)*n))
    return eval_df.nlargest(n_pick, f'{model}_score')['target_strict'].sum()/n_pick

def eval_model(model_n, scored, bs_ids):#, verbose=True, top_n=.05
    top_ns = [0.01, 0.02, 0.03, 0.04, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
    # make dicts to hold results
    total_top_n_ret_d = {}
    total_top_n_def_d = {}
    mbm_top_n_ret_d = {}
    mbm_top_n_def_d = {}
    bsmbm_top_n_ret_d = {}
    bsmbm_top_n_def_d = {}
    
    # overall top_n from whole test population
    for top_n in top_ns:
        top_n_ret = get_topn_ret(model_n, scored, top_n)
        top_n_def = get_topn_def_pct(model_n, scored, top_n)
        total_top_n_ret_d = {top_n: top_n_ret}
        total_top_n_def_d = {top_n: top_n_def}
    
    
    

#     if verbose:
#         print('{0}'.format(model_n))
#         print('topn return: {0}'.format(top_n_ret))
#         print('topn default rate: {0}'.format(top_n_def))
        
    # SAVING ________________________________________________________________    
    # named stuff is non-tracked by dvc
    with open(os.path.join(config.results_dir,'{0}_return.json'.format(model_n)), 'w') as f:
        json.dump(total_top_n_ret_d, f)
    with open(os.path.join(config.results_dir,'{0}_default_rate.json'.format(model_n)), 'w') as f:
        json.dump(total_top_n_def_d, f)
        
    # unnamed version track with dvc
    with open(os.path.join(config.results_dir,'return.json'), 'w') as f:
        json.dump(total_top_n_ret_d, f)
    with open(os.path.join(config.results_dir,'default_rate.json'), 'w') as f:
        json.dump(total_top_n_def_d, f)
    
    

# if results dir doesn't exist, make it
if not os.path.isdir(config.results_dir):
    os.makedirs(config.results_dir)

# load in datasets
scored = pd.read_feather(os.path.join(config.data_dir, 'eval_loan_info_scored.fth'))
# load in train_test_ids.pkl
with open(os.path.join(config.data_dir, 'train_test_ids.pkl'), 'rb') as f:
    train_test_ids = pickle.load(f)
scored = utils.cut_to_ids(scored, train_test_ids['test'])
# load in bootstrap_test_ids.pkl
with open(os.path.join(config.data_dir, 'bootstrap_test_ids.pkl'), 'rb') as f:
    bootstrap_test_ids = pickle.load(f)

eval_model(model_n, scored, bootstrap_test_ids)
    
    
    
