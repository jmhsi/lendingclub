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
# from pandas.testing import assert_frame_equal
from catboost import CatBoostClassifier, CatBoostRegressor
from joblib import load
import pickle

import j_utils.munging as mg
from lendingclub import config

ppath = config.prj_dir
dpath = config.data_dir
mpath = config.modeling_dir


class Model():
    '''
    Model class loads appropriate model based on name in constructor
    Also handles preprocessing
    '''
    def __init__(self, name: str):
        self.name = name
        self.basempath = os.path.join(ppath, 'models')
        self.mpath = os.path.join(self.basempath, self.name)
        self.proc_arti = None
        self.m = None
        self.df = None
        self.load_model()
        
    def load_model(self):
        if self.name in ['baseline', 'A', 'B', 'C', 'D', 'E', 'F', 'G']:
            with open(os.path.join(mpath, '{0}_model.pkl'.format(self.name)), 'rb') as file:
                self.m = pickle.load(file)
        elif self.name == 'logistic_regr':
            self.m = load(os.path.join(mpath, '{0}_model.pkl'.format(self.name)))
            self.proc_arti = load(os.path.join(mpath, '{0}_model_proc_arti.pkl'.format(self.name)))
            

    def score(self, df: pd.DataFrame):
        '''
        Given a dataframe (base_loan_info, non imputed or scaled or normalized)
        return scores. Imputation, Scaling, and Normalizing will be handled
        inside this method to match that done at training
        
        HIGHER SCORES SHOULD BE BETTER (for classification, want prob of
        not defaulting)
        '''
        if (self.df and not self.df.equals(df)) or (not self.df):
            self.df = df
            
        # baselines and grades
        if self.name in ['baseline', 'A', 'B', 'C', 'D', 'E', 'F', 'G']:
            self.prng = np.random.RandomState(self.m)
            scores = self.prng.random(len(df))
            if self.name in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
                mask = np.where(df['grade'] == self.name, 0, 1).astype(bool)
                scores[mask] = 0
            return scores
        elif self.name == 'logistic_regr':
            self.proc_df = mg.val_test_proc(self.df, *self.proc_arti)
            # return probability of not default
            return self.m.predict_proba(self.proc_df)[:, 0]
        print('unknown model??')
        return None
        
def load_scored_df():
    '''
    loads the df with all model scores. If it doesn't exist, creates it
    '''
    path = os.path.join(config.data_dir, 'scored_eval_loan_info.fth')
    if os.path.exists(path):
        return pd.read_feather(path)
    return pd.read_feather(os.path.join(config.data_dir, 'eval_loan_info.fth'))
