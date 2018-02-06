#!/home/justin/anaconda3/bin/python

print('From DL Server, wait invest')
import requests as requests
import json as json
import lendingclub.account_info as acc_info
import re as re
from sklearn.externals import joblib
import lendingclub.dataprep_and_modeling.modeling_utils.data_prep_new as data_prep
import lendingclub.investing.investing_utils as investing_utils
import pandas as pd
import numpy as np
import math as math
from lendingclub.dataprep_and_modeling.model_dump.nn_1_0_1 import net_class
import torch


# constants
nn_path = '/home/justin/justin_tinkering/data_science/lendingclub/dataprep_and_modeling/model_dump/nn_1_0_1/1.0.1_e600'
rf_path = '/home/justin/justin_tinkering/data_science/lendingclub/dataprep_and_modeling/model_dump/model_0.2.1.pkl'
token = acc_info.token
inv_acc_id = acc_info.investor_id
portfolio_id = acc_info.portfolio_id
header = {
    'Authorization': token,
    'Content-Type': 'application/json',
    'X-LC-LISTING-VERSION': '1.2'
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

# Load models
net = net_class.Net()
net.load_state_dict(torch.load(nn_path))
rf = joblib.load(rf_path)

# wait until it is time to do the api call. I'm rate limited to 1 call a second
investing_utils.pause_until_time(test=False)

api_loans, api_ids = investing_utils.get_loans_and_ids(
    header, exclude_already=True)
api_loans = investing_utils.match_col_names(api_loans)
api_loans = investing_utils.match_existing_cols_to_csv(api_loans)
api_loans = investing_utils.make_missing_cols_and_del_dates(api_loans)
api_X, _ = data_prep.process_data_test(api_loans)

# score the api_loans, filter to min score
# net score
nn_api_yhat = net_class.torch_version(api_X, net)
# rf score
rf_api_yhat = rf.predict(api_X)

#combined score
api_yhat = (nn_api_yhat + rf_api_yhat)/2

ids_and_scores = pd.Series(dict(zip(api_ids, api_yhat)))
ids_and_scores = ids_and_scores.sort_values(ascending=False)
loans_to_pick_from = ids_and_scores[ids_and_scores >= min_score]
loans_to_pick_from = loans_to_pick_from.sort_values(ascending=False)

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
print('reached end of invest_script.py')
