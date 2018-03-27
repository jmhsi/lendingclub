# reflects feb 2018 change of open_il_6m to open_act_il
# %load ../dataprep_and_modeling/modeling_utils/data_prep_new.py
import pandas as pd
import numpy as np
from sklearn.externals import joblib
import os as os


home = os.path.expanduser('~')
base_path = home + '/justin_tinkering/data_science/lendingclub/dataprep_and_modeling'


def prep_data_cols(df):
    '''previously determined which columns need to one-hot, mark as null-or-not,
    or leave as is. Returns dataframe with modified columns, ready to standardize.'''
    # Columns that should be in the final df
    must_have_cols = np.array(['loan_amnt', 'term', 'int_rate', 'annual_inc', 'dti', 'delinq_2yrs',
                               'inq_last_6mths', 'open_acc', 'pub_rec', 'revol_bal', 'total_acc',
                               'collections_12_mths_ex_med', 'acc_now_delinq',
                               'chargeoff_within_12_mths', 'delinq_amnt', 'tax_liens',
                               'line_history_m', 'fico', 'maturity_time', 'maturity_paid',
                               'orig_amt_due', 'target_strict', 'target_loose',
                               'installment_amount', 'npv_roi_10', 'grade_A', 'grade_B', 'grade_C',
                               'grade_D', 'grade_E', 'grade_F', 'grade_G', 'sub_grade_A1',
                               'sub_grade_A2', 'sub_grade_A3', 'sub_grade_A4', 'sub_grade_A5',
                               'sub_grade_B1', 'sub_grade_B2', 'sub_grade_B3', 'sub_grade_B4',
                               'sub_grade_B5', 'sub_grade_C1', 'sub_grade_C2', 'sub_grade_C3',
                               'sub_grade_C4', 'sub_grade_C5', 'sub_grade_D1', 'sub_grade_D2',
                               'sub_grade_D3', 'sub_grade_D4', 'sub_grade_D5', 'sub_grade_E1',
                               'sub_grade_E2', 'sub_grade_E3', 'sub_grade_E4', 'sub_grade_E5',
                               'sub_grade_F1', 'sub_grade_F2', 'sub_grade_F3', 'sub_grade_F4',
                               'sub_grade_F5', 'sub_grade_G1', 'sub_grade_G2', 'sub_grade_G3',
                               'sub_grade_G4', 'sub_grade_G5', 'emp_length_1 year',
                               'emp_length_10+ years', 'emp_length_2 years', 'emp_length_3 years',
                               'emp_length_4 years', 'emp_length_5 years', 'emp_length_6 years',
                               'emp_length_7 years', 'emp_length_8 years', 'emp_length_9 years',
                               'emp_length_< 1 year', 'emp_length_n/a', 'home_ownership_mortgage',
                               'home_ownership_other', 'home_ownership_own', 'home_ownership_rent',
                               'verification_status_none', 'verification_status_platform',
                               'verification_status_source', 'purpose_car', 'purpose_credit_card',
                               'purpose_debt_consolidation', 'purpose_educational',
                               'purpose_home_improvement', 'purpose_house',
                               'purpose_major_purchase', 'purpose_medical', 'purpose_moving',
                               'purpose_other', 'purpose_renewable_energy',
                               'purpose_small_business', 'purpose_vacation', 'purpose_wedding',
                               'addr_state_AK', 'addr_state_AL', 'addr_state_AR', 'addr_state_AZ',
                               'addr_state_CA', 'addr_state_CO', 'addr_state_CT', 'addr_state_DC',
                               'addr_state_DE', 'addr_state_FL', 'addr_state_GA', 'addr_state_HI',
                               'addr_state_IA', 'addr_state_ID', 'addr_state_IL', 'addr_state_IN',
                               'addr_state_KS', 'addr_state_KY', 'addr_state_LA', 'addr_state_MA',
                               'addr_state_MD', 'addr_state_ME', 'addr_state_MI', 'addr_state_MN',
                               'addr_state_MO', 'addr_state_MS', 'addr_state_MT', 'addr_state_NC',
                               'addr_state_ND', 'addr_state_NE', 'addr_state_NH', 'addr_state_NJ',
                               'addr_state_NM', 'addr_state_NV', 'addr_state_NY', 'addr_state_OH',
                               'addr_state_OK', 'addr_state_OR', 'addr_state_PA', 'addr_state_RI',
                               'addr_state_SC', 'addr_state_SD', 'addr_state_TN', 'addr_state_TX',
                               'addr_state_UT', 'addr_state_VA', 'addr_state_VT', 'addr_state_WA',
                               'addr_state_WI', 'addr_state_WV', 'addr_state_WY',
                               'application_type_direct_pay', 'application_type_individual',
                               'application_type_joint', 'mths_since_last_delinq_isnull',
                               'mths_since_last_record_isnull', 'revol_util_isnull',
                               'mths_since_last_major_derog_isnull', 'annual_inc_joint_isnull',
                               'dti_joint_isnull', 'tot_coll_amt_isnull', 'tot_cur_bal_isnull',
                               'open_acc_6m_isnull', 'open_act_il_isnull', 'open_il_12m_isnull',
                               'open_il_24m_isnull', 'mths_since_rcnt_il_isnull',
                               'total_bal_il_isnull', 'il_util_isnull', 'open_rv_12m_isnull',
                               'open_rv_24m_isnull', 'max_bal_bc_isnull', 'all_util_isnull',
                               'total_rev_hi_lim_isnull', 'inq_fi_isnull', 'total_cu_tl_isnull',
                               'inq_last_12m_isnull', 'acc_open_past_24mths_isnull',
                               'avg_cur_bal_isnull', 'bc_open_to_buy_isnull', 'bc_util_isnull',
                               'mo_sin_old_il_acct_isnull', 'mo_sin_old_rev_tl_op_isnull',
                               'mo_sin_rcnt_rev_tl_op_isnull', 'mo_sin_rcnt_tl_isnull',
                               'mort_acc_isnull', 'mths_since_recent_bc_isnull',
                               'mths_since_recent_bc_dlq_isnull', 'mths_since_recent_inq_isnull',
                               'mths_since_recent_revol_delinq_isnull',
                               'num_accts_ever_120_pd_isnull', 'num_actv_bc_tl_isnull',
                               'num_actv_rev_tl_isnull', 'num_bc_sats_isnull', 'num_bc_tl_isnull',
                               'num_il_tl_isnull', 'num_op_rev_tl_isnull', 'num_rev_accts_isnull',
                               'num_rev_tl_bal_gt_0_isnull', 'num_sats_isnull',
                               'num_tl_120dpd_2m_isnull', 'num_tl_30dpd_isnull',
                               'num_tl_90g_dpd_24m_isnull', 'num_tl_op_past_12m_isnull',
                               'pct_tl_nvr_dlq_isnull', 'percent_bc_gt_75_isnull',
                               'pub_rec_bankruptcies_isnull', 'tot_hi_cred_lim_isnull',
                               'total_bal_ex_mort_isnull', 'total_bc_limit_isnull',
                               'total_il_high_credit_limit_isnull', 'revol_bal_joint_isnull',
                               'sec_app_inq_last_6mths_isnull', 'sec_app_mort_acc_isnull',
                               'sec_app_open_acc_isnull', 'sec_app_revol_util_isnull',
                               'sec_app_open_act_il_isnull', 'sec_app_num_rev_accts_isnull',
                               'sec_app_chargeoff_within_12_mths_isnull',
                               'sec_app_collections_12_mths_ex_med_isnull',
                               'sec_app_mths_since_last_major_derog_isnull',
                               'age_since_last_delinq', 'age_since_last_record',
                               'age_since_last_major_derog'])

    to_one_hot = ['grade', 'sub_grade', 'emp_length', 'home_ownership',
                  'verification_status', 'purpose', 'addr_state',
                  'application_type',
                  ]
    to_null_or_not = [
        'mths_since_last_delinq', 'mths_since_last_record', 'revol_util',
        'mths_since_last_major_derog', 'annual_inc_joint', 'dti_joint',
        'tot_coll_amt', 'tot_cur_bal', 'open_acc_6m', 'open_act_il',
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
        'sec_app_revol_util', 'sec_app_open_act_il', 'sec_app_num_rev_accts',
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
    for col in to_null_or_not:
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
    # bayesian pca imputing with, or not every imputation option is available
    # in the test set. Might add back in once more data is available. Some of
    # the cols would not be imputed, but instead remain marked via null or not
    # processing. e.g. if someone had no delinquency then I wouldn't try and
    # impute a delinquency.
    to_drop_cols = [
        'issue_d', 'zip_code', 'verification_status_joint',
    ]  # 'mths_since_last_delinq', 'mths_since_last_record','mths_since_last_major_derog',
    copy_df = concated_df.drop(to_drop_cols, axis=1)
    exception_cols = ['annual_inc_joint', 'dti_joint',
                      'pub_rec_bankruptcies', 'revol_util']

    copy_df = copy_df.drop(
        [col for col in to_null_or_not if col not in exception_cols], axis=1)
    copy_df_cols = copy_df.columns.values
    for col in must_have_cols:
        if col not in copy_df_cols:
            # columns that are missing mean that its a categorical and all
            # values in that df should be 0
            copy_df[col] = 0
    # copy_df.dropna(how='any', axis=1, inplace=True)
    copy_df.fillna({'dti':999.0}, inplace=True)
    return copy_df


def target_selection_and_weighting(df, target=None, weights=None, verbose=False):
    '''function to choose target (an npv_roi for regression or target_strict or target_loose for classification) and weights. This function is WIP.'''
    target = ['npv_roi_10'] if not target else [target]
    if verbose == True:
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
    for col in standardized.columns.values:
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
    mean_stddev = joblib.load(base_path + '/model_dump/mean_stddev.pkl')
    mean_series = mean_stddev[0]
    std_dev_series = mean_stddev[1]
    standardized = (standardized - mean_series) / std_dev_series
    return standardized, eval_cols


def process_data_train(df, target=None, weights=None):
    df = prep_data_cols(df)
    return standardize_handle_nans_train(
        *target_selection_and_weighting(df, target=target))


def process_data_test(df, target=None, weights=None):
    df = prep_data_cols(df)
    return standardize_handle_nans_test(
        *target_selection_and_weighting(df, target=target))

if __name__ == '__main__':
    print('This is the dump of utility functions for data preprocessing on Lending Club loans')