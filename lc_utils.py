from typing import List, Union, Optional, Tuple
import pandas as pd
from j_utils import munging as mg


def gen_datasets(today: str,
                 valid_start: str,
                 base_loan_info: pd.DataFrame,
                 eval_loan_info: pd.DataFrame,
                 target: Union[str, List[str]],
                 doneness: float = .95,
                 stat_adj: bool = True,
                 oldest: Optional[str] = None,
                 valid_end: Optional[str] = None,
                 verbose: bool = False,
                 impute: bool = False,) -> Tuple:
    #                 old_and_done: bool = False
    '''
    makes train_x, train_y, valid_x, valid_y, train_ids, valid_ids
    
    
    Args:
        today: string, marks the date. Training data is loans issued btwn @oldest until @today that have
            an end_d < @today
        valid_start: string, date to start validation set from. Must be greater than today and not the same year and month
        base_loan_info: the pandas dataframe of loan info (e.g. X)
        eval_loan_info: the pandas dataframe of target, other eval metrics (e.g. one or more of the columns is y)
        target: define the target column from eval_loan_info
        doneness: maturity time or maturity paid (or stat_adj versions) must be >= than this number
        stat_adj: True or False, choosing whether to use status adjusted values. Default is True
        oldest: Will not use loans that were issued before this date
        valid_end: Will not include loans greater than this date in the validation set
        verbose: for hyperlearn impute. Should be moved outside of this function
        impute: for hyperlearn impute. Should be moved outside of this function
    '''
    
    done_statuses = ['paid', 'charged_off', 'defaulted']
    today = pd.to_datetime(today)
    valid_start = pd.to_datetime(valid_start)
    assert (today < valid_start - pd.to_timedelta(valid_start.day-1, unit='d')),'valid_start must be greater than today and not the same year and month'
    
    # cut loans to required doneness
    if stat_adj:
        eval_loan_info_mask = eval_loan_info.eval('maturity_time_stat_adj >= @doneness or '
                                              'maturity_paid_stat_adj >= @doneness or '
                                              'loan_status == @done_statuses')
    else:
        eval_loan_info_mask = eval_loan_info.eval('maturity_time >= @doneness or '
                                              'maturity_paid >= @doneness or '
                                              'loan_status == @done_statuses')
    
    # specify date bounds of train and valid sets
    if oldest:
        train_mask = eval_loan_info.eval(#'issue_d <= @today and '
                                         'issue_d >= @oldest and '
                                                 'end_d < @today') & eval_loan_info_mask
    else:
        train_mask = eval_loan_info.eval(#'issue_d <= @today and '
                                                 'end_d < @today') & eval_loan_info_mask
    if valid_end:
        valid_mask = eval_loan_info.eval("issue_d >= @valid_start and "
                                         "issue_d <= @valid_end") & eval_loan_info_mask
    else:
        valid_mask = eval_loan_info.eval("issue_d >= @valid_start") & eval_loan_info_mask
        
    train_x = base_loan_info.loc[train_mask]
    valid_x = base_loan_info.loc[valid_mask]
    
    train_ids = train_x['id']
    valid_ids = valid_x['id']
    
    assert len(train_x) == len(train_ids)
    assert len(valid_x) == len(valid_ids)

    if impute:
        import hyperlearn.hyperlearn.impute.SVDImpute as hpl_imp
        # setup for catboost
        # a bit more data processing and nan handling for catboost
        train_copy = train_x.copy()
        valid_copy = valid_x.copy()

        # get ready for hyperlearn svdimpute
        train_copy, max_dict, min_dict, cats_dict, norm_dict = mg.train_hpl_proc(
            train_copy, verbose=verbose)
        valid_copy = mg.val_test_hpl_proc(
            valid_copy, train_copy, max_dict, min_dict, cats_dict, verbose=verbose)

        # fit to train
        S, VT, mean, std, mins, standardise = hpl_imp.fit(train_copy.values)

        # impute on train
        train_svdimp = hpl_imp.transform(
            train_copy.values, S, VT, mean, std, mins, standardise)
        train_svdimp = pd.DataFrame(train_svdimp)
        train_svdimp.index = train_copy.index
        train_svdimp.columns = train_copy.columns

        # impute on test
        valid_svdimp = hpl_imp.transform(
            valid_copy.values, S, VT, mean, std, mins, standardise)
        valid_svdimp = pd.DataFrame(valid_svdimp)
        valid_svdimp.index = valid_copy.index
        valid_svdimp.columns = valid_copy.columns

        # imputing changes some ids. Make the ids the originals again.
        train_svdimp['id'] = train_ids
        valid_svdimp['id'] = valid_ids
        
        train_x = train_svdimp
        valid_x = valid_svdimp

    if type(target) == str:
        target = [target]
    target = ['id'] + target
    
    train_y = eval_loan_info.loc[train_mask, target]
    valid_y = eval_loan_info.loc[valid_mask, target]
        
    assert len(train_x) == len(train_ids) == len(train_y)
    assert len(valid_x) == len(valid_ids) == len(valid_y)
    
    train_x = train_x.sort_values('id')
    valid_x = valid_x.sort_values('id')
    train_y = train_y.sort_values('id')
    valid_y = valid_y.sort_values('id')
    
    assert (train_x['id'] != train_y['id']).sum() == 0
    assert (valid_x['id'] != valid_y['id']).sum() == 0
    
    return train_x, train_y, valid_x, valid_y, train_ids, valid_ids


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

    quantile_date = pd.to_datetime(df[date_column], errors='raise').astype(
        'int64').quantile(q=quantile)  # .astype('datetime64[ns]')

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
    
# Deprecation
# def gen_datasets(today: str,
#                  valid_start: str,
#                  base_loan_info: pd.DataFrame,
#                  eval_loan_info: pd.DataFrame,
#                  target: Union[str, List[str]],
#                  doneness: float = .95,
#                  stat_adj: bool = True,
#                  oldest: Optional[str] = None,
#                  valid_end: Optional[str] = None,
#                  verbose: bool = False,
#                  impute: bool = False) -> Tuple:
#     '''
#     all loans from oldest until today are taken as train. All loans issued after today until valid_end are used for validation. Uses hyperlearn svd_impute to impute missing values. Returns the train and test datasets. target can be single colname or list of colnames.
#     Will take all done loans as well (e.g. loan_status is paid, defaulted, charged_off)
#     Checks that train x/y are same length and order. Does same for valid
#     '''
    
#     # cut loans to required doneness
#     if stat_adj:
#         eval_loan_info = eval_loan_info[(eval_loan_info['maturity_time_stat_adj'] >= doneness) |
#                                     (eval_loan_info['maturity_paid_stat_adj'] >= doneness) |
#                                     (eval_loan_info['loan_status'].isin(['paid', 'charged_off', 'defaulted']))]
#     else:
#         eval_loan_info = eval_loan_info[(eval_loan_info['maturity_time'] >= doneness) |
#                                     (eval_loan_info['maturity_paid'] >= doneness) |
#                                     (eval_loan_info['loan_status'].isin(['paid', 'charged_off', 'defaulted']))]
    
#     # specify date bounds of train and valid sets
#     if oldest:
#         train_ids = eval_loan_info[(eval_loan_info['issue_d'] <= today) & (
#         eval_loan_info['issue_d'] >= oldest)]['id'].unique()
#     else:
#         train_ids = eval_loan_info[eval_loan_info['issue_d'] <= today]['id'].unique()
#     if valid_end:
#         valid_ids = eval_loan_info[(eval_loan_info['issue_d'] >= valid_start) & (
#             eval_loan_info['issue_d'] <= valid_end)]['id'].unique()
#     else:
#         valid_ids = eval_loan_info[(
#             eval_loan_info['issue_d'] >= valid_start)]['id'].unique()
        
#     train_x = base_loan_info[base_loan_info['id'].isin(train_ids)]
#     valid_x = base_loan_info[base_loan_info['id'].isin(valid_ids)]
    
#     assert len(train_x) == len(train_ids)
#     assert len(valid_x) == len(valid_ids)

#     if impute:
#         import hyperlearn.hyperlearn.impute.SVDImpute as hpl_imp
#         # setup for catboost
#         # a bit more data processing and nan handling for catboost
#         train_copy = train_x.copy()
#         valid_copy = valid_x.copy()

#         # get ready for hyperlearn svdimpute
#         train_copy, max_dict, min_dict, cats_dict, norm_dict = mg.train_hpl_proc(
#             train_copy, verbose=verbose)
#         valid_copy = mg.val_test_hpl_proc(
#             valid_copy, train_copy, max_dict, min_dict, cats_dict, verbose=verbose)

#         # fit to train
#         S, VT, mean, std, mins, standardise = hpl_imp.fit(train_copy.values)

#         # impute on train
#         train_svdimp = hpl_imp.transform(
#             train_copy.values, S, VT, mean, std, mins, standardise)
#         train_svdimp = pd.DataFrame(train_svdimp)
#         train_svdimp.index = train_copy.index
#         train_svdimp.columns = train_copy.columns

#         # impute on test
#         valid_svdimp = hpl_imp.transform(
#             valid_copy.values, S, VT, mean, std, mins, standardise)
#         valid_svdimp = pd.DataFrame(valid_svdimp)
#         valid_svdimp.index = valid_copy.index
#         valid_svdimp.columns = valid_copy.columns

#         # imputing changes some ids. Make the ids the originals again.
#         train_svdimp['id'] = train_ids
#         valid_svdimp['id'] = valid_ids
        
#         train_x = train_svdimp
#         valid_x = valid_svdimp

#     if type(target) == str:
#         target = [target]
#     target = ['id'] + target
    
#     train_y = eval_loan_info[eval_loan_info['id'].isin(train_ids)][target]
#     valid_y = eval_loan_info[eval_loan_info['id'].isin(valid_ids)][target]
        
#     assert len(train_x) == len(train_ids) == len(train_y)
#     assert len(valid_x) == len(valid_ids) == len(valid_y)
    
#     train_x.sort_values('id', inplace=True)
#     valid_x.sort_values('id', inplace=True)
#     train_y.sort_values('id', inplace=True)
#     valid_y.sort_values('id', inplace=True)
    
#     assert (train_x['id'] != train_y['id']).sum() == 0
#     assert (valid_x['id'] != valid_y['id']).sum() == 0
    
#     return train_x, train_y, valid_x, valid_y, train_ids, valid_ids

