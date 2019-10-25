import os
import sys
import argparse
import pickle
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from catboost import CatBoostRegressor, CatBoostClassifier
from lendingclub import config, utils
import j_utils.munging as mg

def prepare_data(model_n, data, proc=None, ds_type='train'):
    '''
    returns the processed data for a model, which could be different between
    model types e.g. can handle categoricals or not. additionally returns
    a tuple of anything necessary to process valid/test data in the same manner
    ds_type must be 'train', 'valid', or 'test'
    '''
    assert ds_type in ['train', 'valid', 'test'], print('ds_type invalid')
    if model_n in ['baseline', 'A', 'B', 'C', 'D', 'E', 'F', 'G']:
        return data, None
#     elif model_n == 'logistic_regr':
    else:
        if ds_type == 'train':
            temp = mg.train_proc(data)
            procced = temp[0]
            return procced, temp[1:]
        elif ds_type in ['test', 'valid']:
            assert proc, print('must pass data processing artifacts')
            temp = mg.val_test_proc(data, *proc)
            return temp

    
def train_model(model_n, X_train, y_train, X_valid=None, y_valid=None):
    '''
    Fit model and return model
    '''
    if model_n in ['baseline', 'A', 'B', 'C', 'D', 'E', 'F', 'G']:
        return 42
    elif model_n == 'logistic_regr':
        lr_model = LogisticRegression(class_weight='balanced')
        lr_model.fit(X_train, y_train)
        return lr_model
    elif model_n == 'catboost_regr':
        pass
    elif model_n == 'catboost_clf':
        # basic params
        params = {
            'iterations': 5000,
        #     'one_hot_max_size': 45,
        #     'learning_rate': 0.01,
        #     'has_time': True,
            'eval_metric': 'AUC',#'Recall',
            'random_seed': 42,
            'logging_level': 'Silent',
            'use_best_model': True,
            'task_type': 'GPU',
        #     'boosting_type': 'Ordered',
        #     'loss_function': 'Log',
            'custom_metric': ['F1', 'Precision', 'Recall', 'Accuracy', 'AUC'],
            'od_type': 'Iter',
            'od_wait': 300,
        }
        # get categorical feature indices for catboost
        obj_cols = X_train.select_dtypes(['object', 'datetime']).columns
        categorical_features_indices = [X_train.columns.get_loc(col) for col in obj_cols]
        catboost_clf = CatBoostClassifier(**params)
        catboost_clf.fit(X_train, y_train, cat_features=categorical_features_indices,
                        eval_set=(X_valid, y_valid,), logging_level='Verbose', plot=True) #
        return catboost_clf
        
def export_models(m, model_n):
    if model_n in ['baseline', 'A', 'B', 'C', 'D', 'E', 'F', 'G']:
        with open(os.path.join(config.modeling_dir, '{0}_model.pkl'.format(model_n)), 'wb') as file:
            pickle.dump(m, file)
    elif model_n == 'logistic_regr':
        joblib.dump(m,os.path.join(config.modeling_dir, '{0}_model.pkl'.format(model_n)))
    elif model_n == 'catboost_clf':
        m.save_model(os.path.join(config.modeling_dir, '{0}_model.cb'.format(model_n)))
    
def export_data_processing(proc_arti, model_n):
    if model_n in ['baseline', 'A', 'B', 'C', 'D', 'E', 'F', 'G']:
        with open(os.path.join(config.modeling_dir, '{0}_model_proc_arti.pkl'.format(model_n)), 'wb') as file:
            pickle.dump(proc_arti, file)
    elif model_n in ['logistic_regr', 'catboost_clf']:
        joblib.dump(proc_arti, os.path.join(config.modeling_dir, '{0}_model_proc_arti.pkl'.format(model_n)))


parser = argparse.ArgumentParser()
parser.add_argument('--model', '-m', help='specify model(s) to train')

if not len(sys.argv) > 1:
    models = ['logistic_regr'] # , 'A', 'B', 'C', 'D', 'E', 'F', 'G'

args = parser.parse_args()
if args.model:
    models = args.model.split()
# models = ['logistic_regr']


if not os.path.isdir(config.modeling_dir):
    os.makedirs(config.modeling_dir)

tr_val_base_data, tr_val_eval_data, _ = utils.load_dataset(ds_type='train')
# ensure ordering is correct for time series split
tr_val_base_data, tr_val_eval_data = mg.sort_train_eval(tr_val_base_data, tr_val_eval_data, 'id', 'issue_d')


for model_n in models:
    print('training {0}'.format(model_n))
    # do 3 steps of TS cross validation, with valid size at 5% (20 splits)
    tscv = mg.time_series_data_split(tr_val_eval_data, 'issue_d', 20, 1)
    for tr_idx, val_idx in tscv:
        # split out validation from train_data
        if model_n in ['logistic_regr', 'catboost_clf']:
            y_train = tr_val_eval_data.loc[tr_idx, 'target_loose']
            y_valid = tr_val_eval_data.loc[val_idx, 'target_loose']
        else:
            y_train = tr_val_eval_data.loc[tr_idx, '0.07']
            y_valid = tr_val_eval_data.loc[val_idx, '0.07']
        X_train = tr_val_base_data.loc[tr_idx]
        X_valid = tr_val_base_data.loc[val_idx]
        
        X_train, proc_arti = prepare_data(model_n, X_train, ds_type='train')
        X_valid = prepare_data(model_n, X_valid, proc = proc_arti, ds_type='valid')
        m = train_model(model_n, X_train, y_train, X_valid, y_valid)

        #save stuff
        export_models(m, model_n)
        export_data_processing(proc_arti, model_n)
