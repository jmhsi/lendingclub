import requests
import json
import re
import pandas as pd
import numpy as np
import datetime as dt
import lendingclub.account_info as acc_info
import pause

inv_acc_id = acc_info.investor_id


def pause_until_time(test=False):
    # pause 3 seconds, then print hello world
    now = dt.datetime.now()
    current_hour = now.hour
    if not test:
        pause_until = dt.datetime(
            now.year, now.month, now.day, now.hour + 1, 0, 0)
    if test:
        # if testing, wait 2 seconds and print('will pause 2 seconds')
        pause_until = dt.datetime(
            now.year, now.month, now.day, now.hour, now.minute, now.second + 2)
        print('will pause 2 seconds')
    print('right now it is {0}, pausing until {1}'.format(
        now.strftime('%H:%M:%S'), pause_until.strftime('%H:%M:%S')))
    pause.until(pause_until)


def convert_to_underscore(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([0-9A-Z])', r'\1_\2', s1).lower()


def get_already_invested_filter_id(header):
    filters_list = json.loads(requests.get(
        'https://api.lendingclub.com/api/investor/v1/accounts/' + str(inv_acc_id) + '/filters', headers=header).content)
    filters_df = pd.DataFrame(filters_list['filters'])
    # I manually made a single filter that excludes loans already invested in.
    # Not sure if there is a way to do this entirely through the api.
    return filters_df[filters_df['name'] == 'exclude_already_invested'].iloc[0, 0]


def get_loans_and_ids(header, exclude_already=True):
    '''Gets loans from lendingclub with the single filter of exclude loans already invested in.'''
    if exclude_already:
        filter_id = get_already_invested_filter_id(header)
        payload = {'showAll': 'true', 'filterId': filter_id}
        resp = requests.get(
            'https://api.lendingclub.com/api/investor/v1/loans/listing', headers=header, params=payload)
        loans_list = json.loads(resp.content)['loans']
    if not exclude_already:
        payload = {'showAll': 'true'}
        resp = requests.get(
            'https://api.lendingclub.com/api/investor/v1/loans/listing', headers=header, params=payload)
        loans_list = json.loads(resp.content)['loans']

    api_loans = pd.DataFrame(loans_list)
    api_loans.columns = np.array(
        [convert_to_underscore(col) for col in api_loans.columns.values])
    # save the loan ids
    loan_ids = api_loans['id']
    return api_loans, loan_ids


def match_col_names(api_loans):
    # cols to add
    # make a col of nans so cols match up exactly
    api_loans['issue_d'] = 0
    api_loans['line_history_m'] = 0
    api_loans['maturity_paid'] = 0
    api_loans['maturity_time'] = 0
    api_loans['npv_roi_10'] = 0
    api_loans['orig_amt_due'] = 0
    api_loans['target_loose'] = 0
    api_loans['target_strict'] = 0
    api_loans['fico'] = 0

    cols_to_drop_immediately = [
        'accept_d',
        'credit_pull_d',
        'desc',
        'emp_title',
        'exp_d',
        'exp_default_rate',
        'funded_amount',
        'housing_payment',
        'id',
        'ils_exp_d',
        'initial_list_status',
        'investor_count',
        'list_d',
        'member_id',
        'mtg_payment',
        'review_status',
        'review_status_d',
        'sec_app_earliest_cr_line',
        'sec_app_fico_range_high',
        'sec_app_fico_range_low',
        'service_fee_rate',
    ]
    api_loans.drop(cols_to_drop_immediately, axis=1, inplace=True)
    rename_dict = {
        'acc_open_past_24_mths': 'acc_open_past_24mths',
        'addr_zip': 'zip_code',
        'delinq_2_yrs': 'delinq_2yrs',
        'i_l_util': 'il_util',
        'inq_last_6_mths': 'inq_last_6mths',
        'installment': 'installment_amount',
        'is_inc_v': 'verification_status',
        'is_inc_v_joint': 'verification_status_joint',
        'loan_amount': 'loan_amnt',
        'num_accts_ever_12_0_ppd': 'num_accts_ever_120_pd',
        'num_tl_12_0dpd_2m': 'num_tl_120dpd_2m',
        'sec_app_inq_last_6_mths': 'sec_app_inq_last_6mths',
    }
    api_loans.rename(columns=rename_dict, inplace=True)
    return api_loans


def match_existing_cols_to_csv(api_loans):
    api_loans.fillna(value=np.nan, inplace=True)
    api_loans['all_util'] = api_loans['all_util'] / 100.0
    api_loans['application_type'] = api_loans['application_type'].str.lower()

    # turn employment length into categorical
    emp_len_dict = {np.nan: 'n/a',
                    0.0: '< 1 year',
                    12.0: '1 year',
                    24.0: '2 years',
                    36.0: '3 years',
                    48.0: '4 years',
                    60.0: '5 years',
                    72.0: '6 years',
                    84.0: '7 years',
                    96.0: '8 years',
                    108.0: '9 years',
                    120.0: '10+ years', }
    api_loans['emp_length'] = api_loans['emp_length'].replace(emp_len_dict)
    api_loans['home_ownership'] = api_loans['home_ownership'].str.lower()
    api_loans['int_rate'] = api_loans['int_rate'] / 100.0

    # verification status
    dic_veri_status = {'NOT_VERIFIED': 'none',
                       'SOURCE_VERIFIED': 'source',
                       'VERIFIED': 'platform'}
    api_loans['verification_status'] = api_loans[
        'verification_status'].replace(dic_veri_status)
    api_loans['verification_status_joint'] = api_loans[
        'verification_status_joint'].replace(dic_veri_status)
    api_loans['pct_tl_nvr_dlq'] = api_loans['pct_tl_nvr_dlq'] / 100.0
    api_loans['percent_bc_gt_75'] = api_loans['percent_bc_gt_75'] / 100.0
    api_loans['revol_util'] = api_loans['revol_util'] / 100.0
    return api_loans


def make_missing_cols_and_del_dates(api_loans):
    # probably something with earliest credit line, fico range high/low
    # need to add line_history_m, orig_amt_due, fico
    api_loans['fico'] = (api_loans['fico_range_high'] +
                         api_loans['fico_range_low']) / 2
    # line_history_m depends on issue_d, which doesn't exist for listed loans.
    # Assume it takes one month to issue so increase the number compared to
    # the csvs by 1
    today = pd.to_datetime(dt.date.today())
    api_loans['earliest_cr_line'] = pd.to_datetime(
        api_loans['earliest_cr_line'])
    line_hist_d = (today - api_loans['earliest_cr_line']) / np.timedelta64(
        1, 'D')
    api_loans['line_history_m'] = (line_hist_d * (12 / 365.25)).round() + 1
    api_loans['orig_amt_due'] = api_loans[
        'term'] * api_loans['installment_amount']

    api_loans.drop(['earliest_cr_line', 'fico_range_high',
                    'fico_range_low'], axis=1, inplace=True)
    return api_loans


def verify_df_base_cols(api_loans, test_loans):
    api_cols = api_loans.columns.values.copy()
    api_cols.sort()
    csv_cols = test_loans.columns.values.copy()
    csv_cols.sort()
    assert len(api_cols) == len(csv_cols)
    examine = dict(zip(api_cols, csv_cols))
    for key, val in examine.iteritems():
        if key != val:
            print(key, val)
            return None
    return True
