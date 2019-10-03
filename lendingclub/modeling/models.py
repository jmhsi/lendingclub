'''
Defines the Model class and methods.
Usage:
    Instantiate a model:
        baseline = Model('baseline')
    Get scores for a dataframe:
        scores = baseline.score(df)
'''


import os

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier, CatBoostRegressor
from joblib import load

import j_utils.munging as mg
from lendingclub import config

ppath = config.prj_dir
dpath = config.data_dir
mpath = config.model_dir


class Model():
    '''
    Model class loads appropriate model based on name in constructor
    Also handles preprocessing
    '''
    def __init__(self, name: str):
        self.name = name
        self.basempath = os.path.join(ppath, 'models')
        self.mpath = os.path.join(self.basempath, self.name)
        self.m = None
        self.df = None

    def score(self, df: pd.DataFrame):
        '''
        Given a dataframe (base_loan_info, non imputed or scaled or normalized)
        return scores. Imputation, Scaling, and Normalizing will be handled
        inside this method to match that done at training
        '''
        # baselines and grades
        if self.name == 'baseline':
            return np.random.random(len(df))
        elif self.name in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
            scores = np.random.random(len(df))
            mask = np.where(df['grade'] == self.name, 0, 1).astype(bool)
            scores[mask] = 0
            return scores
        # logistic regression
        elif self.name == 'logistic_regr':
            self.m = load(os.path.join(self.mpath, 'logistic_regr.joblib'))
            self.proc_data(df)
            preds = self.m.predict_proba(self.df)[:, 0]
            return preds
        # catboost classifier
        elif self.name == 'catboost_clf':
            catboost_clf = CatBoostClassifier()
            catboost_clf.load_model(os.path.join(self.mpath,
                                                 'catboost_clf.cb'))
            self.m = catboost_clf
            self.proc_data(df)
            preds = self.m.predict_proba(self.df)[:, 0]
            return preds
        # catboost classifier
        elif self.name == 'catboost_clf_cbdp':
            catboost_clf = CatBoostClassifier()
            catboost_clf.load_model(os.path.join(self.mpath,
                                                 'catboost_clf.cb'))
            self.m = catboost_clf
            self.proc_data_cb(df)
            preds = self.m.predict_proba(self.df)[:, 0]
            return preds
        # catboost regressor
        elif self.name == 'catboost_regr':
            catboost_regr = CatBoostRegressor()
            catboost_regr.load_model(
                os.path.join(self.mpath, 'catboost_regr.cb'))
            self.m = catboost_regr
            self.proc_data(df)
            preds = self.m.predict(self.df)
            return preds
        # catboost regressor
        elif self.name == 'catboost_regr_cbdp':
            catboost_regr = CatBoostRegressor()
            catboost_regr.load_model(
                os.path.join(self.mpath, 'catboost_regr.cb'))
            self.m = catboost_regr
            self.proc_data_cb(df)
            preds = self.m.predict(self.df)
            return preds
        print('unknown model??')
        return None

    def proc_data_cb(self, df):
        '''
        process data before passing it as input for training.
        For catboost, letting catboost deal with categoricals
        '''
        date_cols = df.select_dtypes('datetime')
        for col in date_cols:
            df[col] = df[col].astype('str')
        self.df = df

    def proc_data(self, df):
        '''
        process data before passing it as input for training.
        Uses the j_utils.munging process data format, and requires loading
        7 pickles of colnames, max/mins,
        fill values, categorical mappings, and numbers needed for normalizing
        '''
        assert 'end_d' not in df, print(
            'must pass base_loan_info, not eval_loan_info')
        self.df = df
        all_train_colnames = load(
            os.path.join(self.mpath, 'all_train_colnames.joblib'))
        max_dict = load(os.path.join(self.mpath, 'max_dict.joblib'))
        min_dict = load(os.path.join(self.mpath, 'min_dict.joblib'))
#         new_null_colnames = load(
#             os.path.join(self.mpath, 'new_null_colnames.joblib'))
        fill_dict = load(os.path.join(self.mpath, 'fill_dict.joblib'))
        cats_dict = load(os.path.join(self.mpath, 'cats_dict.joblib'))
        norm_dict = load(os.path.join(self.mpath, 'norm_dict.joblib'))
        self.df = mg.val_test_proc(df, all_train_colnames, max_dict, min_dict,
                                   fill_dict, cats_dict, norm_dict)
