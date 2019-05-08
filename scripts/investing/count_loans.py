#import requests
from datetime import datetime
import json
import lendingclub.account_info as acc_info
import re
import lendingclub.dataprep_and_modeling.modeling_utils.data_prep_new as data_prep
import lendingclub.investing.investing_utils as investing_utils
import pandas as pd

# constants
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

print(datetime.utcnow().strftime('%Y-%m-%d:%H-%M-%S.%f')[:-3])
api_loans, api_ids = investing_utils.get_loans_and_ids(
    header, exclude_already=True)
print(len(api_ids))
print(datetime.utcnow().strftime('%Y-%m-%d:%H-%M-%S.%f')[:-3])
