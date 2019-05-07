import pandas as pd
from j_utils import munging as mg
import hyperlearn.hyperlearn.impute.SVDImpute as hpl_imp

def gen_expt_datasets(today, oldest, valid_start, base_loan_info, eval_loan_info, target, valid_end=None, verbose=False):
    '''
    all loans from oldest until today are taken as train. All loans issued after today until valid_end are used for validation. Uses hyperlearn svd_impute to impute missing values. Returns the train and test datasets. target can be single colname or list of colnames
    '''
    train_ids = eval_loan_info[(eval_loan_info['issue_d'] <= today) & (eval_loan_info['issue_d'] >= oldest)]['id'].unique()
    if valid_end:
        valid_ids = eval_loan_info[(eval_loan_info['issue_d'] >= valid_start) & (eval_loan_info['issue_d'] <= valid_end)]['id'].unique()
    else:
        valid_ids = eval_loan_info[(eval_loan_info['issue_d'] >= valid_start)]['id'].unique()
    train = base_loan_info[base_loan_info['id'].isin(train_ids)]
    valid = base_loan_info[base_loan_info['id'].isin(valid_ids)]
    
    # setup for catboost
    # a bit more data processing and nan handling for catboost
    train_copy = train.copy()
    valid_copy = valid.copy()
    
    # get ready for hyperlearn svdimpute
    train_copy, max_dict, min_dict, cats_dict, norm_dict = mg.train_hpl_proc(train_copy, verbose=verbose)
    valid_copy = mg.val_test_hpl_proc(valid_copy, train_copy, max_dict, min_dict, cats_dict, verbose=verbose)

    # fit to train
    S, VT, mean, std, mins, standardise = hpl_imp.fit(train_copy.values)
    
    # impute on train
    train_svdimp = hpl_imp.transform(train_copy.values, S, VT, mean, std, mins, standardise)
    train_svdimp = pd.DataFrame(train_svdimp)
    train_svdimp.index = train_copy.index
    train_svdimp.columns = train_copy.columns
    
    # impute on test
    valid_svdimp = hpl_imp.transform(valid_copy.values, S, VT, mean, std, mins, standardise)
    valid_svdimp = pd.DataFrame(valid_svdimp)
    valid_svdimp.index = valid_copy.index
    valid_svdimp.columns = valid_copy.columns
    
    # imputing changes some ids. Make the ids the originals again.
    train_svdimp['id'] = train_ids
    valid_svdimp['id'] = valid_ids
    
    train_y = eval_loan_info[eval_loan_info['id'].isin(train_ids)][target]
    valid_y = eval_loan_info[eval_loan_info['id'].isin(valid_ids)][target]
    
    return train_svdimp, train_y, valid_svdimp, valid_y, train_ids, valid_ids

# make a crude test set for now
def get_split_date(df, date_column, quantile): 

    """
    https://stackoverflow.com/questions/31018622/pandas-quantile-function-for-dates
    Get the date on which to split a dataframe for timeseries splitting
    Adjusted coerce param to errors since SO is old.
    """ 

    # 1. convert date_column to datetime (useful in case it is a string) 
    # 2. convert into int (for sorting) 
    # 3. get the quantile 
    # 4. get the corresponding date
    # 5. return, pray that it works 

    quantile_date = pd.to_datetime(df[date_column], errors = 'raise').astype('int64').quantile(q=quantile)#.astype('datetime64[ns]')

    return pd.to_datetime(quantile_date)

def split_out_traintestable_loans(df, eval_df, oldness_thrsh=.9):
    '''Can train/test on loans that pass the oldness_thrsh or have status paid/defaulted/charged_off'''
    old_enough_ids = eval_df[(eval_df['maturity_time_stat_adj'] >= oldness_thrsh) | 
                                    (eval_df['maturity_paid_stat_adj'] >= oldness_thrsh) | 
                                    (eval_df['loan_status'].isin(['paid', 'defaulted', 'charged_off']))]['id'].unique()
    df = df[df['id'].isin(old_enough_ids)]
    eval_df = eval_df[eval_df['id'].isin(old_enough_ids)]
    return df, eval_df


def add_custom_lc_features(df):
    # added features
    df['monthly_inc'] = df['annual_inc'] / 12
    df['dti_w_loan'] = (df['dti'] * df['monthly_inc'] +
                                    df['installment']) / df['monthly_inc']
    df['delinq_to_monthly_inc'] = df['delinq_amnt'] / \
        df['monthly_inc']
    df['tot_cur_bal_to_monthly_inc'] = df['tot_cur_bal'] / \
        df['monthly_inc']
    df['loan_to_inc'] = df['loan_amount'] / \
        df['monthly_inc']