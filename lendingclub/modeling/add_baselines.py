import os
import pandas as pd
from lendingclub.modeling.models import Model, load_scored_df
from lendingclub import config

dpath = config.data_dir
base_loan_info = pd.read_feather(os.path.join(dpath, 'base_loan_info.fth'))
eval_loan_info = load_scored_df()

for model in ['baseline', 'A', 'B', 'C', 'D', 'E', 'F', 'G']:
    m = Model(model)
    eval_loan_info['{0}_score'.format(model)] = m.score(base_loan_info)
    
eval_loan_info.to_feather(os.path.join(dpath, 'eval_loan_info_scored.fth'))
