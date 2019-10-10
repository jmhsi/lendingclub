import os
import pickle
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
from lendingclub import config
from lendingclub.lc_utils import gen_datasets

parser = argparse.ArgumentParser()
parser.add_argument('--model', '-m', help='specify model(s) to train')

if not len(sys.argv) > 1:
    models = ['baseline'] # , 'A', 'B', 'C', 'D', 'E', 'F', 'G'

def get_topn_ret(model, eval_df, n, return_col='0.07', bootstrap=False):
    '''
    Picks loans and get returns based on maximizing model_score
    '''
    assert n <= 1
    assert n >= 0
    if bootstrap:
        eval_df = eval_df.sample(frac=1, replace=True)
    return eval_df.nlargest(int(round(len(eval_df)*n)), f'{model}_score')['0.07'].mean()

def get_topn_def_pct(model, eval_df, n, bootstrap=False):
    '''
    get the def percents with the top_n
    '''
    assert n <= 1
    assert n >= 0
    if bootstrap:
        eval_df = eval_df.sample(frac=1, replace=True)
    n_pick = int(round(len(eval_df)*n))
    return eval_df.nlargest(n_pick, f'{model}_score')['target_strict'].sum()/n_pick

# if results dir doesn't exist, make it
if not os.path.isdir(config.results_dir):
    os.makedirs(config.results_dir)

# load in datasets
scored = pd.read_feather(os.path.join(config.data_dir, 'eval_loan_info_scored.fth'))

for model_n in models:
    top_n_ret = get_topn_ret(model_n, scored, .5,)
    top_n_def = get_topn_def_pct(model_n, scored, .5,)
    
    print('{0}'.format(model_n))
    print('topn return: {0}'.format(top_n_ret))
    print('topn default rate: {0}'.format(top_n_def))
    # named stuff is non-tracked by dvc
    with open(os.path.join(config.results_dir,'{0}_return.txt'.format(model_n)), 'w+') as f:
        f.write("{0}".format(top_n_ret))
    with open(os.path.join(config.results_dir,'{0}_default_rate.txt'.format(model_n)), 'w+') as f:
        f.write("{0}".format(top_n_def))
        
    # unnamed version track with dvc
    with open(os.path.join(config.results_dir,'return.txt'), 'w+') as f:
        f.write("{0}".format(top_n_ret))
    with open(os.path.join(config.results_dir,'default_rate.txt'), 'w+') as f:
        f.write("{0}".format(top_n_def))
