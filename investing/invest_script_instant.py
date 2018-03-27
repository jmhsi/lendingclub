print('From DL Server, wait invest')
import requests as requests
import json as json
import lendingclub.account_info as acc_info
import re as re
from sklearn.externals import joblib
import lendingclub.dataprep_and_modeling.modeling_utils.data_prep_new as data_prep
import lendingclub.investing.investing_utils as investing_utils
from investing_utils import StandardScalerJustin
import pandas as pd
import numpy as np
import math as math
import torch
import pickle as pickle


# constants
token = acc_info.token
inv_acc_id = acc_info.investor_id
portfolio_id = acc_info.portfolio_id
header = {
    'Authorization': token,
    'Content-Type': 'application/json',
    'X-LC-LISTING-VERSION': '1.3'
}
acc_summary_url = 'https://api.lendingclub.com/api/investor/v1/accounts/' + \
    str(inv_acc_id) + '/summary'
order_url = 'https://api.lendingclub.com/api/investor/v1/accounts/' + \
    str(inv_acc_id) + '/orders'
min_score = -0.02  # -0.04599714276994965  # -0.035764345824470828
inv_amt = 25.00
cash_limit = 0.00

# First check if I have enough money that I want to invest. min 10 notes so 250
summary_dict = json.loads(requests.get(
    acc_summary_url, headers=header).content)
cash_to_invest = summary_dict['availableCash']

# Load models and things for models
# RF
rf = investing_utils.load_RF()
with open(f'{investing_utils.data_save_path}/for_proc_df_model_loading.pkl', 'rb') as handle:
    nas_all_train, embeddings_all_train, train_cols_meds_all_train, use_cols, cols_all_train, col_cat_dict, mean_stdev_mapper_all_train, dl_df_train, dl_ys_train, cat_vars, emb_szs = pickle.load(handle)
    
# process the dataframe before I'm able to set up the neural net _____________
# wait until it is time to do the api call. I'm rate limited to 1 call a second
investing_utils.pause_until_time(test=True)

# get the loans and process the dataframe
api_loans, api_ids = investing_utils.get_loans_and_ids(
    header, exclude_already=True)

# cut api loans to cols that are cols I'll need
api_ori_use_cols = [col for col in api_loans.columns if col in use_cols]
api_loans = api_loans[api_ori_use_cols]
api_loans['fake_ys'] = -999
date_cols = ['earliest_cr_line', 'sec_app_earliest_cr_line']
for col in date_cols:
    api_loans[col] = pd.to_datetime(api_loans[col]).apply(lambda dt: dt.replace(day=1))
investing_utils.add_dateparts(api_loans)    
investing_utils.train_cats(api_loans)
ordered_cat_cols = ['grade', 'sub_grade']
for col in col_cat_dict.keys():
    if col in ordered_cat_cols:
        ordered = True
    else:
        ordered = False
    api_loans[col] = pd.Categorical(api_loans[col], categories = col_cat_dict[col], ordered = ordered)
X_test, y_test, nas, _, mean_stdev_mapper = investing_utils.proc_df_justin(api_loans, 'fake_ys', valid_test = True, do_scale=True, na_dict=nas_all_train, mapper = mean_stdev_mapper_all_train, train_cols_meds=train_cols_meds_all_train, cols=cols_all_train)
# fake a last row for val_idxs for X_test and y_test
fake_row = pd.DataFrame(X_test.shape[1]*[-999]).T
fake_row.columns=X_test.columns
X_test = X_test.append(fake_row)
y_test = np.append(y_test, np.array([-999]))

# setup NN and load saved weights
md = investing_utils.ColumnarModelData.from_data_frame(investing_utils.PATH_NN, val_idxs=[len(X_test)-1], df=X_test, y=y_test, cat_flds=cat_vars, bs=1000, test_df=X_test.iloc[:-1,:])
n_cont = len(dl_df_train.columns)-len(cat_vars)
nn = md.get_learner(emb_szs, n_cont, 0.05, 1, [1000,500,500,250,250], [0.2,0.2,.2,.15,.05])
nn.load(f'{investing_utils.PATH_NN}{investing_utils.regr_version_NN}_{investing_utils.training_type}.pth')

# score the api_loans, filter to min score
# net score
nn_api_yhat = nn.predict(is_test=True)
nn_api_yhat = nn_api_yhat.reshape(-1)
# rf score
rf_api_yhat = rf.predict(X_test.iloc[:-1,:])
#combined score
api_yhat = (nn_api_yhat + rf_api_yhat)/2

# matching scores and loans
ids_and_scores = pd.DataFrame(pd.Series(dict(zip(api_ids, api_yhat))))
def get_preds(RF): return RF.predict(X_test.iloc[:-1,:])
preds = np.stack(investing_utils.parallel_trees(rf, get_preds))
CIs = investing_utils.make_CIs(preds)
ids_and_scores = pd.DataFrame(ids_and_scores)
ids_and_scores.rename(columns={0:'3.0.0_score'}, inplace=True)
ids_and_scores['rf_mean'] = CIs['mean'].values
ids_and_scores['rf_std_dev'] = CIs['std_dev'].values
ids_and_scores = ids_and_scores.sort_values('3.0.0_score',ascending=False)
loans_to_pick_from = ids_and_scores[ids_and_scores['3.0.0_score'] >= min_score]
loans_to_pick_from = loans_to_pick_from.sort_values('3.0.0_score', ascending=False)

# See how many loans to pick from, set up order
n_to_pick = int(math.floor(cash_to_invest / inv_amt))
to_order_loan_ids = loans_to_pick_from[:n_to_pick].index.values
orders_dict = {'aid': inv_acc_id}
orders_list = []
for loan_ids in to_order_loan_ids:
    orders_list.append({'loanId': int(loan_ids),
                        'requestedAmount': int(inv_amt),
                        'portfolioId': int(portfolio_id)})
orders_dict['orders'] = orders_list
payload = json.dumps(orders_dict)
if cash_to_invest >= cash_limit:
    order_response = requests.post(order_url, headers=header, data=payload)
else:
    print('Cash to invest is ${0}. Waiting for at least ${1} cash before investing'.format(
        cash_to_invest, cash_limit))

print('Ran investment round.')
print('Cash to invest: ${0}, meaning {1} possible notes to invest in at ${2} each.'.format(
    cash_to_invest, n_to_pick, inv_amt))
print('{0} loans seen through api, of which {1} could be ordered due to score or cash available. Min score cutoff is {2}'.format(
    len(api_loans), len(to_order_loan_ids), min_score))
print('Scores from this batch was: {0}'.format(ids_and_scores))
print('Below is from response')
try:
    print(order_response, order_response.content)
except:
    print('No response because no POST of orders')
print('reached end of invest_script_instant.py')