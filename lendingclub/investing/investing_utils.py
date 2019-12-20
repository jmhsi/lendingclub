# %load ../../lendingclub/investing/investing_utils
import requests
import json
import re
import pandas as pd
import numpy as np
import datetime as dt
import user_creds.account_info as acc_info
import pause
import smtplib
from sklearn.base import TransformerMixin, BaseEstimator
from pandas_summary import DataFrameSummary
# from sklearn.externals import joblib

class StandardScalerJustin(TransformerMixin, BaseEstimator):
    def __init__(self, copy=True, with_mean=True, with_std=True):
        self.with_mean = with_mean
        self.with_std = with_std
        self.copy = copy
    
    def fit(self, X, y=None):
        if type(X) == np.ndarray:
            X = pd.Series(X.reshape(-1))
        self.mean_ = X.dropna().mean()
        self.var_ = X.dropna().var()
        return self

    def transform(self, X):
        mean = self.mean_
        std_dev = np.sqrt(self.var_)
        if std_dev == 0:
            return X
        return (X-mean)/std_dev
    
def fit_scalers(df, mapper):
    warnings.filterwarnings('ignore', category=sklearn.exceptions.DataConversionWarning)
    if mapper is None:
        map_f = [([n],StandardScalerJustin()) for n in df.columns if is_numeric_dtype(df[n])]
        mapper = DataFrameMapper(map_f).fit(df)
    return mapper    

def proc_df_justin(df, y_fld, valid_test, skip_flds=None, do_scale=False, na_dict=None,
            preproc_fn=None, max_n_cat=None, subset=None, mapper=None, train_cols_meds=None, cols=None):

    """ proc_df takes a data frame df and splits off the response variable, and
    changes the df into an entirely numeric dataframe.

    Parameters:
    -----------
    df: The data frame you wish to process.

    y_fld: The name of the response variable
    
    valid_test: boolean indicating if this is a df to match to train columns.

    skip_flds: A list of fields that dropped from df.

    do_scale: Standardizes each column in df,Takes Boolean Values(True,False)

    na_dict: a dictionary of na columns to add. Na columns are also added if there
        are any missing values.

    preproc_fn: A function that gets applied to df.

    max_n_cat: The maximum number of categories to break into dummy values, instead
        of integer codes.

    subset: Takes a random subset of size subset from df.

    mapper: If do_scale is set as True, the mapper variable
        calculates the values used for scaling of variables during training time(mean and standard deviation).
        
    train_cols_meds: dict where keys are columns from training and values are medians, use for values to fill an entire missing column (shouldn't be needed when used to actually pick loans, was needed for train/valid/test due to new fields being added over the timeframe and missing in certain datasets while existing in others)
    
    cols: Just to compare column order and ensure the variables are in the right order.

    Returns:
    --------
    [x, y, nas, mapper(optional)]:

        x: x is the transformed version of df. x will not have the response variable
            and is entirely numeric.

        y: y is the response variable

        nas: returns a dictionary of which nas it created, and the associated median.

        mapper: A DataFrameMapper which stores the mean and standard deviation of the corresponding continous
        variables which is then used for scaling of during test-time."""        
    assert type(valid_test) == bool, print('must indiciate if this is test/valid set to match columns with train')
    
    if not skip_flds: skip_flds=[]
    if subset: df = get_sample(df,subset)
    df = df.copy()
    if preproc_fn: preproc_fn(df)
    y = df[y_fld].values
    df.drop(skip_flds+[y_fld], axis=1, inplace=True)

    # fit the scalers
    if do_scale: mapper = fit_scalers(df, mapper)
    if na_dict is None: na_dict = {}      
    for n,c in df.items(): na_dict = fix_missing(df, c, n, na_dict)
    df[mapper.transformed_names_] = mapper.transform(df)
    embeddings=[]
    for n,c in df.items():
        numericalize(df, c, n, max_n_cat)
        if not is_numeric_dtype(c):
            embeddings.append(prep_embeddings(c, n))
    df = pd.get_dummies(df, dummy_na=True)
    # fix the nas
    if valid_test:
        for col, med in train_cols_meds.items():
            try:
                df[col].fillna(med, inplace=True)
            except KeyError:
                print(col)
                df[col] = med
        df = df[cols]
        
    res = [df, y, na_dict, embeddings]
    if not valid_test: res += [res[0].median(), res[0].columns]
    if do_scale: res = res + [mapper]
    return res

def prep_embeddings(c, n):
    # allocate in embeddings for a null
    return (n, len(c.cat.categories)+1)

def eval_models(trials, port_size, available_loans, regr_version, X_test, y_test,
                default_series, yhat_test): #regr, 
    results = {}
    pct_default = {}
    test_copy = X_test.copy()
    
    default_series = default_series.loc[X_test.index]
    yhats_ys_defs = pd.DataFrame([yhat_test, y_test, default_series.values]).T
    yhats_ys_defs.rename(columns={0:'yhat', 1:'y', 2:'defaults'}, inplace=True)
    for trial in tqdm_notebook(np.arange(trials)):
        # of all test loans, grab a batch of n=available_loans
        available_idx = np.random.choice(
            np.arange(len(test_copy)), available_loans, replace=False)
        available_loans_df = yhats_ys_defs.ix[available_idx,:]
        available_loans_df.sort_values('yhat', inplace=True, ascending=False)
        picks = available_loans_df[:port_size]
        results[trial] = picks['y'].mean()
        pct_default[trial] = picks['defaults'].sum()/port_size
    pct_default_series = pd.Series(pct_default)
    results_df = pd.DataFrame(pd.Series(results))
    results_df['pct_def'] = pct_default_series
    results_df.columns = pd.MultiIndex(levels=[[regr_version], [0.07, 'pct_def']],
           labels=[[0, 0,], [0, 1,]],
           names=['discount_rate', 'model'])
    return results_df

# def load_RF():
#     return joblib.load(f'{PATH_RF}{regr_version_RF}_{training_type}.pkl')
    
def add_dateparts(df):
    '''Uses the fastai add_datepart to turn datetimes into numbers to process
       does not do it for issue_d'''
    date_cols = df.select_dtypes(['datetime64']).columns
    for date_col in date_cols:
        if date_col not in special_cols:
            add_datepart(df, date_col, drop=True)
    return [col for col in date_cols if col not in special_cols]    

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
#         print('will pause 2 seconds')
#     print('right now it is {0}, pausing until {1}'.format(
#         now.strftime('%H:%M:%S'), pause_until.strftime('%H:%M:%S')))
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
            'https://api.lendingclub.com/api/investor/v1/loans/listing', headers=header, params=payload) #'https://api.lendingclub.com/api/investor/v1/loans/listing'
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

def make_CIs(preds):
    means = np.mean(preds, axis=0)
    std_devs = np.std(preds, axis=0)
    df = pd.DataFrame(np.zeros((preds.shape[1],2)), columns=['mean', 'std_dev'])
    df['mean'] = means
    df['std_dev'] = std_devs
    return df

def submit_lc_order(cash_to_invest, cash_limit, order_url, header, payload):
    if cash_to_invest >= cash_limit:
        order_response = requests.post(order_url, headers=header, data=payload)
        return order_response
    return None

def send_emails(now, my_gmail_account, my_gmail_password, msg): #, my_recipients
#     subject = now.strftime("%Y-%m-%d %H:%M:%S.%f") + ' Investment Round'
    smtpserver = smtplib.SMTP('smtp.gmail.com',587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.login(my_gmail_account, my_gmail_password)
#     msg = """From: %s\nTo: %s\nSubject: %s\n\n%s""" % (my_gmail_account, my_recipients, subject, message)
#     smtpserver.sendmail(msg)#my_gmail_account, my_recipients, 
    smtpserver.send_message(msg)
    smtpserver.close()

# constants
inv_acc_id = acc_info.investor_id
special_cols = []
platform = 'lendingclub'
datapath = '/home/justin/all_data/'
PATH_NN = f'{datapath}{platform}/NN/'
PATH_RF = f'{datapath}{platform}/RF/'
data_save_path = f'{datapath}{platform}/'
training_type = 'all'
regr_version_RF = '0.2.2'
regr_version_NN = '1.0.1'
