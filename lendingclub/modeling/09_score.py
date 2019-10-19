import os
import pickle
import sys
import argparse

import numpy as np
import pandas as pd
import seaborn as sns
# testing
from pandas.testing import assert_frame_equal
from tqdm import tqdm

import j_utils.munging as mg
from lendingclub.lc_utils import gen_datasets
from lendingclub import config
from lendingclub.modeling.models import Model

parser = argparse.ArgumentParser()
parser.add_argument('--model', '-m', help='specify model(s) to train')

if not len(sys.argv) > 1:
    models = ['baseline'] # , 'A', 'B', 'C', 'D', 'E', 'F', 'G'

args = parser.parse_args()
if args.model:
    models = args.model.split()    
    
    
# load in relevant dataframes
base_loan_info = pd.read_feather(os.path.join(config.data_dir, 'base_loan_info.fth'))
try:
    eval_loan_info = pd.read_feather(os.path.join(config.data_dir, 'eval_loan_info_scored.fth'))
    print('found an existing eval_loan_info_scored.fth to add scores')
    all_scores = pd.read_feather(os.path.join(config.data_dir, 'all_eval_loan_info_scored.fth'))
    print('found an existing all_eval_loan_info_scored.fth to add scores')
except:
    eval_loan_info = pd.read_feather(os.path.join(config.data_dir, 'eval_loan_info.fth'))
    print('no existing eval_loan_info_scored.fth')
    print('this is the first time adding scores')
    all_scores = pd.read_feather(os.path.join(config.data_dir, 'eval_loan_info.fth'))
    print('no existing all_eval_loan_info_scored.fth')
    print('this is the first time adding scores')
    
# check that loans are all in correct order
assert (base_loan_info['id'] == eval_loan_info['id']).all()

# score relevant dataframes
for model_n in models:
    m = Model(model_n)
    scores = m.score(base_loan_info)
    eval_loan_info['{0}_score'.format(model_n)] = scores
    all_scores['{0}_score'.format(model_n)] = scores
    
print('saving scored dataframe at {0}'.format(os.path.join(config.data_dir,'eval_loan_info_scored.fth')))
eval_loan_info.to_feather(os.path.join(config.data_dir,'eval_loan_info_scored.fth'))
print('saving dvc non-tracked scored dataframe at {0}'.format(os.path.join(config.data_dir,'all_eval_loan_info_scored.fth')))
eval_loan_info.to_feather(os.path.join(config.data_dir,'all_eval_loan_info_scored.fth'))
