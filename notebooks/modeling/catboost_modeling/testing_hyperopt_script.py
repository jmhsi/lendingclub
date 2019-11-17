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
from torch import tensor, nn
from hyperopt import fmin, tpe, hp, STATUS_OK, STATUS_FAIL, Trials

def cross_entropy(X,y):
    """
    X is the output from fully connected layer (num_examples x num_classes)
    y is labels (num_examples x 1)
    	Note that y is not one-hot encoded vector. 
    	It can be computed as y.argmax(axis=1) from one-hot encoded vectors of labels if required.
    """
    m = y.shape[0]
    p = X
    # We use multidimensional array indexing to extract 
    # softmax probability of the correct label for each sample.
    # Refer to https://docs.scipy.org/doc/numpy/user/basics.indexing.html#indexing-multi-dimensional-arrays for understanding multidimensional array indexing.
    log_likelihood = -np.log(p[range(m),y])
    loss = np.sum(log_likelihood) / m
    return loss

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

class HPOpt(object):

    def __init__(self, x_train, x_test, y_train, y_test):
        self.x_train = x_train
        self.x_test  = x_test
        self.y_train = y_train
        self.y_test  = y_test

    def process(self, fn_name, space, trials, algo, max_evals):
        fn = getattr(self, fn_name)
#         try:
        result = fmin(fn=fn, space=space, algo=algo, max_evals=max_evals, trials=trials)
#         except Exception as e:
#             return {'status': STATUS_FAIL,
#                     'exception': str(e)}
        return result, trials

#     def xgb_reg(self, para):
#         reg = xgb.XGBRegressor(**para['reg_params'])
#         return self.train_reg(reg, para)

#     def lgb_reg(self, para):
#         reg = lgb.LGBMRegressor(**para['reg_params'])
#         return self.train_reg(reg, para)

    def ctb_regr(self, para):
        reg = CatBoostRegressor(**para['regr_params'])
        return self.train_reg(reg, para)
    
    def ctb_clf(self, para):
        clf = CatBoostClassifier(**para['clf_params'])
        return self.train_clf(clf, para)

    def train_reg(self, reg, para):
        reg.fit(self.x_train, self.y_train,
                eval_set=(self.x_test, self.y_test),
                **para['fit_params'])
        pred = reg.predict(self.x_test)
        loss = para['loss_func'](self.y_test, pred)
        return {'loss': loss, 'status': STATUS_OK}
    
    def train_clf(self, clf, para):
        clf.fit(self.x_train, self.y_train,
                eval_set=(self.x_test, self.y_test),
                **para['fit_params'])
        pred = clf.predict_proba(self.x_test)
        loss = para['loss_func'](pred, self.y_test.values)
        return {'loss': loss, 'status': STATUS_OK}



model_n = 'catboost_clf'
loss = cross_entropy   
    
# CatBoost parameters
ctb_clf_params = {
    'learning_rate': hp.choice('learning_rate', np.geomspace(.005, .5, num=5)),
#     'max_depth': hp.choice('max_depth', np.arange(1,16, 1)),
#     'colsample_bylevel': hp.choice('colsample_bylevel',
#                                    np.arange(0.1, 1.0, 0.1)),
    'n_estimators': 10,
    'eval_metric': hp.choice('eval_metric', ['Logloss', 'CrossEntropy']),
    'task_type':'GPU',
}
ctb_fit_params = {'early_stopping_rounds': 5, 'verbose': False}
ctb_para = dict()
ctb_para['clf_params'] = ctb_clf_params
ctb_para['fit_params'] = ctb_fit_params
ctb_para['loss_func'] = loss

loss(np.array([[1,0], [0,1]]), np.array([0,1]))

tr_val_base_data, tr_val_eval_data, _ = utils.load_dataset(ds_type='train')
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

X_train.shape

obj = HPOpt(X_train, X_valid, y_train, y_valid)
ctb_opt = obj.process(fn_name='ctb_clf', space=ctb_para, trials=Trials(), algo=tpe.suggest, max_evals=10)
