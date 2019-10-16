import os
import pickle
import json
import sys
from typing import List
import argparse
import tqdm

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
    
args = parser.parse_args()
if args.model:
    models = args.model.split()    

def get_topn_ret(model, eval_df, n, return_col='0.07'): 
    '''
    Picks loans and get returns based on maximizing model_score
    '''
    return get_topn(model, eval_df, n)['0.07'].mean()

def get_topn(model, eval_df, n):
    assert n <= 1
    assert n >= 0
    n_pick = max(1,int(round(len(eval_df)*n)))
    return eval_df.nlargest(n_pick, f'{model}_score')

def get_roi_simple(model, eval_df, n):
    df = get_topn(model, eval_df, n)
    # divide roi_simple by weighted average term to get
    # a rough estimate of the month's return
    waterm = df['term'].mean()
    waret = df['roi_simple'].mean() 
    m_ret = waret/waterm
#     print(df['issue_d'].max(), df['issue_d'].min())
#     print(waterm, waret, m_ret)
    return m_ret

def get_topn_def_pct(model, eval_df, n): #, bootstrap=False
    '''
    get the def percents with the top_n
    '''
    return get_topn(model, eval_df, n)['target_strict'].mean()

def dump_named(f_name, dic, m_name, add_m_name=False):
    if add_m_name:
        f_name = '{0}_{1}'.format(m_name, f_name)
    with open(os.path.join(config.results_dir, f_name), 'w+') as f:
        json.dump(dic, f)

def eval_model(model_n, test, bs_idx, debug=False):#, verbose=True, top_n=.05
    top_ns = [0.01, 0.02, 0.03, 0.04, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
    issue_d_gr = test.groupby('issue_d')
    # make dicts to hold results
    total_top_n_ret_d = {}
    total_top_n_def_d = {}
    mbm_top_n_ret_d = {}
    mbm_top_n_def_d = {}
    smbm_top_n_ret_d = {}
#     bsmbm_top_n_ret_d = {}
#     bsmbm_top_n_def_d = {}
    
    for n in tqdm(top_ns):
        print("FOR TOP_N: {0}".format(n))
         # overall top_n from whole test population
        top_n_ret = round(get_topn_ret(model_n, test, n), 4)
        top_n_def = round(get_topn_def_pct(model_n, test, n), 4)
        
        # month by month over all of test loans
        temp_mbm = {}
        temp_mbm_def = {}
        temp_smbm_ret = {}
        for d, g in issue_d_gr:
            temp_mbm[d] = get_topn_ret(model_n, g, n)
            temp_mbm_def[d] = get_topn_def_pct(model_n, g, n)
            temp_smbm_ret[d] = get_roi_simple(model_n, g, n)
            
        # single mbm return
        start = 0
        err = 10e-10
        for d, r in temp_smbm_ret.items():
#             print(r, np.log(r))
#             print(start)
            start += np.log(r+err)
        
        smbm_top_n_ret_d[n] = round(np.exp(start)**(1/len(temp_smbm_ret)),4)
        
#         # get bsmbm
#         temp_bsmbm = {}
#         temp_bsmbm_def = {}
#         for i, idx in bs_idx.items():
#             temp = {}
#             temp_def = {}
#             df = test.loc[idx]
#             for d, g in df.groupby('issue_d'):
#                 temp[d] = get_topn_ret(model_n, g, n)
#                 temp_def[d] = get_topn_def_pct(model_n, g, n)
#             temp_bsmbm[i] = temp
#             temp_bsmbm_def[i] = temp_def
        
        
#         bsmbm_top_n_ret_d[n] = temp_bsmbm
#         bsmbm_top_n_def_d[n] = temp_bsmbm_def
        mbm_top_n_ret_d[n] = temp_mbm
        mbm_top_n_def_d[n] = temp_mbm_def
        total_top_n_ret_d[n] = top_n_ret
        total_top_n_def_d[n] = top_n_def
        
    # summarize to save
    mbm_top_n_ret_json = pd.DataFrame(mbm_top_n_ret_d).describe().round(4).T.to_json()
    mbm_top_n_def_json = pd.DataFrame(mbm_top_n_def_d).describe().round(4).T.to_json()


        
    # SAVING ________________________________________________________________    
    # named and unnamed version for tracking
    if debug:
        return bsmbm_top_n_ret_d, bsmbm_top_n_def_d, mbm_top_n_ret_d, mbm_top_n_def_d, smbm_top_n_ret_d
    
    if not debug:
        for add_m_name in [True, False]:
            dump_named('return.json', total_top_n_ret_d, model_n, add_m_name=add_m_name)
            dump_named('default_rate.json', total_top_n_def_d, model_n, add_m_name=add_m_name)
            dump_named('mbm_return.json', mbm_top_n_ret_json, model_n, add_m_name=add_m_name)
            dump_named('mbm_default_rate.json', mbm_top_n_def_json, model_n, add_m_name=add_m_name)
            dump_named('smbm_return.json', smbm_top_n_ret_d, model_n, add_m_name=add_m_name)
        
#         metrics = {'accuracy': '99.5'}
#         with open(os.path.join(config.results_dir,'test.json'), 'w') as f:
#             json.dump(metrics, f)
        
#             dump_named('bsmbm_return.json', total_top_n_ret_d, model_n, add_m_name=add_m_name)
#             dump_named('bsmbm_default_rate.json', total_top_n_def_d, model_n, add_m_name=add_m_name)
    

# if results dir doesn't exist, make it
if not os.path.isdir(config.results_dir):
    os.makedirs(config.results_dir)

# load in datasets
test = pd.read_feather(os.path.join(config.data_dir, 'eval_loan_info_scored.fth'))
# load in train_test_ids.pkl
with open(os.path.join(config.data_dir, 'train_test_ids.pkl'), 'rb') as f:
    train_test_ids = pickle.load(f)
test = utils.cut_to_ids(test, train_test_ids['test'])
# load in bootstrap_test_ids.pkl
with open(os.path.join(config.data_dir, 'bootstrap_test_idx.pkl'), 'rb') as f:
    bootstrap_test_ids = pickle.load(f)

# do the evaling
for model_n in models:
    eval_model(model_n, test, bootstrap_test_ids)

# # # debugging
# bsmbm_top_n_ret_d, bsmbm_top_n_def_d, mbm_top_n_ret_d, mbm_top_n_def_d, smbm_top_n_ret_d = eval_model(model_n, test, bootstrap_test_ids, debug=True)
    
    
    
