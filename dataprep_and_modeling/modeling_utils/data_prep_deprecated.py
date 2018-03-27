import pandas as pd
import numpy as np
from tqdm import tqdm_notebook
from sklearn.externals import joblib


def prep_data_cols(df):
    '''previously determined which columns need to one-hot, mark as null-or-not,
    or leave as is. Returns dataframe with modified columns, ready to standardize.'''

    to_one_hot = ['grade', 'sub_grade', 'emp_length', 'home_ownership',
                  'verification_status', 'purpose', 'addr_state',
                  'application_type',
                  ]
    to_null_or_not = [
        'mths_since_last_delinq', 'mths_since_last_record', 'revol_util',
        'mths_since_last_major_derog', 'annual_inc_joint', 'dti_joint',
        'tot_coll_amt', 'tot_cur_bal', 'open_acc_6m', 'open_il_6m',
        'open_il_12m', 'open_il_24m', 'mths_since_rcnt_il', 'total_bal_il',
        'il_util', 'open_rv_12m', 'open_rv_24m', 'max_bal_bc', 'all_util',
        'total_rev_hi_lim', 'inq_fi', 'total_cu_tl', 'inq_last_12m',
        'acc_open_past_24mths', 'avg_cur_bal', 'bc_open_to_buy', 'bc_util',
        'mo_sin_old_il_acct', 'mo_sin_old_rev_tl_op', 'mo_sin_rcnt_rev_tl_op',
        'mo_sin_rcnt_tl', 'mort_acc', 'mths_since_recent_bc',
        'mths_since_recent_bc_dlq', 'mths_since_recent_inq',
        'mths_since_recent_revol_delinq', 'num_accts_ever_120_pd',
        'num_actv_bc_tl', 'num_actv_rev_tl', 'num_bc_sats', 'num_bc_tl',
        'num_il_tl', 'num_op_rev_tl', 'num_rev_accts', 'num_rev_tl_bal_gt_0',
        'num_sats', 'num_tl_120dpd_2m', 'num_tl_30dpd', 'num_tl_90g_dpd_24m',
        'num_tl_op_past_12m', 'pct_tl_nvr_dlq', 'percent_bc_gt_75',
        'pub_rec_bankruptcies', 'tot_hi_cred_lim', 'total_bal_ex_mort',
        'total_bc_limit', 'total_il_high_credit_limit', 'revol_bal_joint',
        'sec_app_inq_last_6mths', 'sec_app_mort_acc', 'sec_app_open_acc',
        'sec_app_revol_util', 'sec_app_open_il_6m', 'sec_app_num_rev_accts',
        'sec_app_chargeoff_within_12_mths',
        'sec_app_collections_12_mths_ex_med',
        'sec_app_mths_since_last_major_derog'
    ]
    do_nothing = [
        'loan_amnt', 'term', 'int_rate', 'annual_inc', 'issue_d', 'dti',
        'delinq_2yrs', 'inq_last_6mths', 'open_acc', 'pub_rec', 'revol_bal',
        'total_acc', 'collections_12_mths_ex_med', 'acc_now_delinq',
        'chargeoff_within_12_mths', 'delinq_amnt', 'tax_liens',
        'line_history_m', 'fico', 'maturity_time', 'maturity_paid',
        'orig_amt_due', 'target_strict', 'target_loose', 'installment_amount', 'zip_code', 'verification_status_joint',
        'npv_roi_10'
    ]

    keep_dfs = [df[do_nothing]]
    null_or_not_df = df[to_null_or_not].copy()
    one_hot_df = pd.get_dummies(df[to_one_hot])
    for col in tqdm_notebook(to_null_or_not):
        one_hot_df[col + '_isnull'] = np.where(null_or_not_df[col].isnull(), 1,
                                               0)
    keep_dfs.append(null_or_not_df)
    keep_dfs.append(one_hot_df)
    concated_df = pd.concat(keep_dfs, axis=1)

    # rescale the mths_since_last_delinq to be from 0,1 0 meaning just had delinq,
    # 1 meaning haven't had delinq since start of credit history
    concated_df['age_since_last_delinq'] = np.where(
        concated_df['mths_since_last_delinq'].isnull(), 1,
        concated_df['mths_since_last_delinq'] /
        concated_df['line_history_m'])

    concated_df['age_since_last_record'] = np.where(
        concated_df['mths_since_last_record'].isnull(), 1,
        concated_df['mths_since_last_record'] /
        concated_df['line_history_m'])

    concated_df['age_since_last_major_derog'] = np.where(
        concated_df['mths_since_last_major_derog'].isnull(), 1,
        concated_df['mths_since_last_major_derog'] /
        concated_df['line_history_m'])

    # dealing with filling from another column because very few nans
    concated_df['annual_inc_joint'] = np.where(
        concated_df['annual_inc_joint'].isnull(), concated_df[
            'annual_inc'],
        concated_df['annual_inc_joint'])

    concated_df['dti_joint'] = np.where(concated_df['dti_joint'].isnull(),
                                        concated_df['dti'],
                                        concated_df['dti_joint'])

    concated_df['pub_rec_bankruptcies'] = np.where(
        concated_df['pub_rec_bankruptcies'].isnull(), concated_df[
            'pub_rec'],
        concated_df['pub_rec_bankruptcies'])

    # if revol bal is 0, revol util is 0, else is 1
    concated_df['revol_util'] = np.where(
        (concated_df['revol_util'].isnull()) &
        (concated_df['revol_bal'] == 0), 0,
        np.where(concated_df['revol_util'].isnull(), 1,
                 concated_df['revol_util']))

    # dropping some cols that I still need to figure out how to do
    # bayesian pca imputing with
    to_drop_cols = [
        'mths_since_last_delinq', 'mths_since_last_record',
        'mths_since_last_major_derog', 'issue_d', 'zip_code', 'verification_status_joint',
    ]
    copy_df = concated_df.drop(to_drop_cols, axis=1)
    copy_df.dropna(how='any', axis=1, inplace=True)
    return copy_df


def target_selection_and_weighting(df, target=None, weights=None):
    '''function to choose target (an npv_roi for regression or target_strict or target_loose for classification) and weights. This function is WIP.'''
    target = ['npv_roi_10'] if not target else [target]
    print('target cols: {0}'.format(target))
    drop_cols_eval_variants = [
        'target_loose', 'target_strict', 'maturity_time', 'maturity_paid', 'npv_roi_10']
    drop_cols_eval_variants = [
        col for col in drop_cols_eval_variants if col not in target]
    copy_df = df.drop(drop_cols_eval_variants, axis=1)
    return copy_df, target


def standardize_handle_nans_train(df, target):
    standardized = df.copy()
    eval_cols = standardized[target]
    standardized.drop(target, axis=1, inplace=True)
    mean_dict = {}
    std_dev_dict = {}
    for col in tqdm_notebook(standardized.columns.values):
        mean = df[col].mean()
        std_dev = df[col].std()
        mean_dict[col] = mean
        std_dev_dict[col] = std_dev
    mean_series = pd.Series(mean_dict)
    std_dev_series = pd.Series(std_dev_dict)
    standardized = (standardized - mean_series) / std_dev_series
    return (standardized, eval_cols, mean_series, std_dev_series)


def standardize_handle_nans_test(df, target):
    standardized = df.copy()
    standardized.fillna(0, inplace=True)
    eval_cols = standardized[target]
    standardized.drop(target, axis=1, inplace=True)
    mean_stddev = joblib.load('model_dump/mean_stddev.pkl')
    mean_series = mean_stddev[0]
    std_dev_series = mean_stddev[1]
    standardized = (standardized - mean_series) / std_dev_series
    return standardized, eval_cols


def process_data_train(df, target=None, weights=None):
    df = prep_data_cols(df)
    return standardize_handle_nans_train(
        *target_selection_and_weighting(df))


def process_data_test(df, target=None, weights=None):
    df = prep_data_cols(df)
    return standardize_handle_nans_test(
        *target_selection_and_weighting(df))

    # class TargetError(Exception):

    #     def __init__(self, value):
    #         self.value = value)
    #     def __str__(self):
    #         return repr(self.value)

if __name__ == '__main__':
    print('This is the dump of utility functions for data preprocessing on Lending Club loans')
