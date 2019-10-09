import os
import pickle
import sys

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

# load in relevant dataframes
base_loan_info = pd.read_feather(os.path.join(config.data_dir, 'base_loan_info.fth'))
try:
    eval_loan_info = pd.read_feather(os.path.join(config.data_dir, 'eval_loan_info_scored.fth'))
    print('found an existing eval_loan_info_scored.fth to add scores')
except:
    eval_loan_info = pd.read_feather(os.path.join(config.data_dir, 'eval_loan_info.fth'))
    print('no existing eval_loan_info_scored.fth')
    print('this is the first time adding scores')
    
# check that loans are all in correct order
assert (base_loan_info['id'] == eval_loan_info['id']).all()

# score relevant dataframes
models = ['baseline', 'A', 'B', 'C', 'D', 'E', 'F', 'G']
for model_n in models:
    m = Model(model_n)
    eval_loan_info['{0}_score'.format(model_n)] = m.score(base_loan_info)
    
print('saving scored dataframe at {0}'.format(os.path.join(config.data_dir,'eval_loan_info_scored.fth')))
eval_loan_info.to_feather(os.path.join(config.data_dir,'eval_loan_info_scored.fth'))
