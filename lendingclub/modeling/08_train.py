import os
import sys
import argparse
import pickle
import numpy as np
import pandas as pd
from lendingclub import config, utils

parser = argparse.ArgumentParser()
parser.add_argument('--model', '-m', help='specify model(s) to train')

if not len(sys.argv) > 1:
    models = ['baseline', 'A', 'B', 'C', 'D', 'E', 'F', 'G']

args = parser.parse_args()
if args.model:
    models = args.model.split()

def prepare_data(model_n, data):
    if model_n in ['baseline', 'A', 'B', 'C', 'D', 'E', 'F', 'G']:
        return data, None
    
def train_model(model_n):
    if model_n in ['baseline', 'A', 'B', 'C', 'D', 'E', 'F', 'G']:
        return 42
    
def export_models(m, model_n):
    if model_n in ['baseline', 'A', 'B', 'C', 'D', 'E', 'F', 'G']:
        with open(os.path.join(config.modeling_dir, '{0}_model.pkl'.format(model_n)), 'wb') as file:
            pickle.dump(m, file)
    
def export_data_processing(data_proc, model_n):
    if model_n in ['baseline', 'A', 'B', 'C', 'D', 'E', 'F', 'G']:
        with open(os.path.join(config.modeling_dir, '{0}_model_dataproc.pkl'.format(model_n)), 'wb') as file:
            pickle.dump(data_proc, file)

if not os.path.isdir(config.modeling_dir):
    os.makedirs(config.modeling_dir)

train_data, _, _ = utils.load_dataset(ds_type='train')

for model_n in models:
    procced_data, data_proc = prepare_data(model_n, train_data)
    m = train_model(model_n)
#     print(model_n, m, type(m))
    
    #save stuff
    export_models(m, model_n)
    export_data_processing(data_proc, model_n)
