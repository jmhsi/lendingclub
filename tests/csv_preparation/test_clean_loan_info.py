'''
Tests for clean_loan_info.py which contains functions used in 04_clean_loan_info.py
'''
import numpy as np
import pandas as pd
import pandas.api.types as ptypes
from lendingclub.csv_preparation import clean_loan_info as cli


def test_loan_info_fmt_date():
    test_cases = [
        pd.DataFrame({
            'id': {
                856: 141066548
            },
            'grade': {
                856: 'A'
            },
            'sub_grade': {
                856: 'A4'
            },
            'emp_title': {
                856: 'Remote Storage Cataloger'
            },
            'emp_length': {
                856: '10+ years'
            },
            'home_ownership': {
                856: 'MORTGAGE'
            },
            'verification_status': {
                856: 'Not Verified'
            },
            'issue_d': {
                856: 'Sep-2018'
            },
            'loan_status': {
                856: 'Current'
            },
            'pymnt_plan': {
                856: 'n'
            },
            'url': {
                856:
                'https://lendingclub.com/browse/loanDetail.action?loan_id=141066548'
            },
            'desc': {
                856: np.nan
            },
            'purpose': {
                856: 'credit_card'
            },
            'title': {
                856: 'Credit card refinancing'
            },
            'zip_code': {
                856: '488xx'
            },
            'addr_state': {
                856: 'MI'
            },
            'earliest_cr_line': {
                856: 'Sep-1978'
            },
            'revol_util': {
                856: '27.3%'
            },
            'initial_list_status': {
                856: 'w'
            },
            'last_pymnt_d': {
                856: 'Aug-2019'
            },
            'next_pymnt_d': {
                856: 'Sep-2019'
            },
            'last_credit_pull_d': {
                856: 'Aug-2019'
            },
            'application_type': {
                856: 'Individual'
            },
            'verification_status_joint': {
                856: np.nan
            },
            'sec_app_earliest_cr_line': {
                856: np.nan
            },
            'hardship_flag': {
                856: 'N'
            },
            'hardship_type': {
                856: np.nan
            },
            'hardship_reason': {
                856: np.nan
            },
            'hardship_status': {
                856: np.nan
            },
            'hardship_start_date': {
                856: np.nan
            },
            'hardship_end_date': {
                856: np.nan
            },
            'payment_plan_start_date': {
                856: np.nan
            },
            'hardship_loan_status': {
                856: np.nan
            },
            'debt_settlement_flag': {
                856: 'N'
            },
            'debt_settlement_flag_date': {
                856: np.nan
            },
            'settlement_status': {
                856: np.nan
            },
            'settlement_date': {
                856: np.nan
            },
            'loan_amnt': {
                856: 13000.0
            },
            'funded_amnt': {
                856: 13000.0
            },
            'funded_amnt_inv': {
                856: 13000.0
            },
            'term': {
                856: 36
            },
            'int_rate': {
                856: 7.840000152587891
            },
            'installment': {
                856: 406.4200134277344
            },
            'annual_inc': {
                856: 67000.0
            },
            'dti': {
                856: 20.030000686645508
            },
            'delinq_2yrs': {
                856: 0.0
            },
            'fico_range_low': {
                856: 760.0
            },
            'fico_range_high': {
                856: 764.0
            },
            'inq_last_6mths': {
                856: 1.0
            },
            'mths_since_last_delinq': {
                856: np.nan
            },
            'mths_since_last_record': {
                856: np.nan
            },
            'open_acc': {
                856: 11.0
            },
            'pub_rec': {
                856: 0.0
            },
            'revol_bal': {
                856: 13573.0
            },
            'total_acc': {
                856: 21.0
            },
            'out_prncp': {
                856: 9688.9501953125
            },
            'out_prncp_inv': {
                856: 9688.9501953125
            },
            'total_pymnt': {
                856: 4067.0400390625
            },
            'total_pymnt_inv': {
                856: 4067.0400390625
            },
            'total_rec_prncp': {
                856: 3311.050048828125
            },
            'total_rec_int': {
                856: 755.989990234375
            },
            'total_rec_late_fee': {
                856: 0.0
            },
            'recoveries': {
                856: 0.0
            },
            'collection_recovery_fee': {
                856: 0.0
            },
            'last_pymnt_amnt': {
                856: 406.4200134277344
            },
            'last_fico_range_high': {
                856: 794.0
            },
            'last_fico_range_low': {
                856: 790.0
            },
            'collections_12_mths_ex_med': {
                856: 0.0
            },
            'mths_since_last_major_derog': {
                856: np.nan
            },
            'policy_code': {
                856: 1.0
            },
            'annual_inc_joint': {
                856: np.nan
            },
            'dti_joint': {
                856: np.nan
            },
            'acc_now_delinq': {
                856: 0.0
            },
            'tot_coll_amt': {
                856: 0.0
            },
            'tot_cur_bal': {
                856: 108625.0
            },
            'open_acc_6m': {
                856: 1.0
            },
            'open_act_il': {
                856: 2.0
            },
            'open_il_12m': {
                856: 1.0
            },
            'open_il_24m': {
                856: 1.0
            },
            'mths_since_rcnt_il': {
                856: 10.0
            },
            'total_bal_il': {
                856: 18068.0
            },
            'il_util': {
                856: 48.0
            },
            'open_rv_12m': {
                856: 2.0
            },
            'open_rv_24m': {
                856: 2.0
            },
            'max_bal_bc': {
                856: 2846.0
            },
            'all_util': {
                856: 36.0
            },
            'total_rev_hi_lim': {
                856: 49800.0
            },
            'inq_fi': {
                856: 1.0
            },
            'total_cu_tl': {
                856: 6.0
            },
            'inq_last_12m': {
                856: 3.0
            },
            'acc_open_past_24mths': {
                856: 4.0
            },
            'avg_cur_bal': {
                856: 9875.0
            },
            'bc_open_to_buy': {
                856: 35392.0
            },
            'bc_util': {
                856: 13.0
            },
            'chargeoff_within_12_mths': {
                856: 0.0
            },
            'delinq_amnt': {
                856: 0.0
            },
            'mo_sin_old_il_acct': {
                856: 216.0
            },
            'mo_sin_old_rev_tl_op': {
                856: 480.0
            },
            'mo_sin_rcnt_rev_tl_op': {
                856: 5.0
            },
            'mo_sin_rcnt_tl': {
                856: 5.0
            },
            'mort_acc': {
                856: 2.0
            },
            'mths_since_recent_bc': {
                856: 5.0
            },
            'mths_since_recent_bc_dlq': {
                856: np.nan
            },
            'mths_since_recent_inq': {
                856: 5.0
            },
            'mths_since_recent_revol_delinq': {
                856: np.nan
            },
            'num_accts_ever_120_pd': {
                856: 0.0
            },
            'num_actv_bc_tl': {
                856: 2.0
            },
            'num_actv_rev_tl': {
                856: 3.0
            },
            'num_bc_sats': {
                856: 6.0
            },
            'num_bc_tl': {
                856: 7.0
            },
            'num_il_tl': {
                856: 8.0
            },
            'num_op_rev_tl': {
                856: 8.0
            },
            'num_rev_accts': {
                856: 11.0
            },
            'num_rev_tl_bal_gt_0': {
                856: 3.0
            },
            'num_sats': {
                856: 11.0
            },
            'num_tl_120dpd_2m': {
                856: 0.0
            },
            'num_tl_30dpd': {
                856: 0.0
            },
            'num_tl_90g_dpd_24m': {
                856: 0.0
            },
            'num_tl_op_past_12m': {
                856: 3.0
            },
            'pct_tl_nvr_dlq': {
                856: 100.0
            },
            'percent_bc_gt_75': {
                856: 0.0
            },
            'pub_rec_bankruptcies': {
                856: 0.0
            },
            'tax_liens': {
                856: 0.0
            },
            'tot_hi_cred_lim': {
                856: 168943.0
            },
            'total_bal_ex_mort': {
                856: 31641.0
            },
            'total_bc_limit': {
                856: 40700.0
            },
            'total_il_high_credit_limit': {
                856: 37696.0
            },
            'revol_bal_joint': {
                856: np.nan
            },
            'sec_app_fico_range_low': {
                856: np.nan
            },
            'sec_app_fico_range_high': {
                856: np.nan
            },
            'sec_app_inq_last_6mths': {
                856: np.nan
            },
            'sec_app_mort_acc': {
                856: np.nan
            },
            'sec_app_open_acc': {
                856: np.nan
            },
            'sec_app_revol_util': {
                856: np.nan
            },
            'sec_app_open_act_il': {
                856: np.nan
            },
            'sec_app_num_rev_accts': {
                856: np.nan
            },
            'sec_app_chargeoff_within_12_mths': {
                856: np.nan
            },
            'sec_app_collections_12_mths_ex_med': {
                856: np.nan
            },
            'sec_app_mths_since_last_major_derog': {
                856: np.nan
            },
            'deferral_term': {
                856: np.nan
            },
            'hardship_amount': {
                856: np.nan
            },
            'hardship_length': {
                856: np.nan
            },
            'hardship_dpd': {
                856: np.nan
            },
            'orig_projected_additional_accrued_interest': {
                856: np.nan
            },
            'hardship_payoff_balance_amount': {
                856: np.nan
            },
            'hardship_last_payment_amount': {
                856: np.nan
            },
            'settlement_amount': {
                856: np.nan
            },
            'settlement_percentage': {
                856: np.nan
            },
            'settlement_term': {
                856: np.nan
            }
        })
    ]
    test_col = 'issue_d'
    cli.loan_info_fmt_date(test_cases[0], test_col)
    assert ptypes.is_datetime64_any_dtype(test_cases[0][test_col])


def test_apply_end_d():
    test_cases = [
        pd.DataFrame({
            'last_pymnt_d': {
                105800: pd.NaT
            },
            'issue_d': {
                105800: pd.Timestamp('2018-07-01 00:00:00')
            },
            'loan_status': {
                105800: 'charged_off'
            },
            'total_pymnt': {
                105800: 3495.889892578125
            },
            'total_pymnt_inv': {
                105800: 3495.889892578125
            },
            'total_rec_prncp': {
                105800: 0.0
            },
            'total_rec_int': {
                105800: 0.0
            },
            'total_rec_late_fee': {
                105800: 0.0
            },
            'recoveries': {
                105800: 3495.889892578125
            },
            'collection_recovery_fee': {
                105800: 629.2601928710938
            },
            'last_pymnt_amnt': {
                105800: 0.0
            }
        }),
        pd.DataFrame({
            'last_pymnt_d': {
                49998: pd.Timestamp('2018-10-01 00:00:00')
            },
            'issue_d': {
                49998: pd.Timestamp('2018-08-01 00:00:00')
            },
            'loan_status': {
                49998: 'charged_off'
            },
            'total_pymnt': {
                49998: 216.10000610351562
            },
            'total_pymnt_inv': {
                49998: 216.10000610351562
            },
            'total_rec_prncp': {
                49998: 124.16000366210938
            },
            'total_rec_int': {
                49998: 91.94000244140625
            },
            'total_rec_late_fee': {
                49998: 0.0
            },
            'recoveries': {
                49998: 0.0
            },
            'collection_recovery_fee': {
                49998: 0.0
            },
            'last_pymnt_amnt': {
                49998: 111.37000274658203
            }
        }),
        pd.DataFrame({
            'last_pymnt_d': {
                7565: pd.Timestamp('2019-07-01 00:00:00')
            },
            'issue_d': {
                7565: pd.Timestamp('2018-09-01 00:00:00')
            },
            'loan_status': {
                7565: 'paid'
            },
            'total_pymnt': {
                7565: 5585.24609375
            },
            'total_pymnt_inv': {
                7565: 5585.25
            },
            'total_rec_prncp': {
                7565: 4800.0
            },
            'total_rec_int': {
                7565: 785.25
            },
            'total_rec_late_fee': {
                7565: 0.0
            },
            'recoveries': {
                7565: 0.0
            },
            'collection_recovery_fee': {
                7565: 0.0
            },
            'last_pymnt_amnt': {
                7565: 53.5
            }
        }), pd.DataFrame({
            'last_pymnt_d': {
                856: pd.Timestamp('2019-08-01 00:00:00')
            },
            'issue_d': {
                856: pd.Timestamp('2018-09-01 00:00:00')
            },
            'loan_status': {
                856: 'current'
            },
            'total_pymnt': {
                856: 4067.0400390625
            },
            'total_pymnt_inv': {
                856: 4067.0400390625
            },
            'total_rec_prncp': {
                856: 3311.050048828125
            },
            'total_rec_int': {
                856: 755.989990234375
            },
            'total_rec_late_fee': {
                856: 0.0
            },
            'recoveries': {
                856: 0.0
            },
            'collection_recovery_fee': {
                856: 0.0
            },
            'last_pymnt_amnt': {
                856: 406.4200134277344
            }
        })
    ]
    max_date = pd.Timestamp('2019-08-01')
    assert cli.apply_end_d('charged_off', test_cases[0],
                           max_date).iat[0] == pd.Timestamp('2018-12-01')
    assert cli.apply_end_d('charged_off', test_cases[1],
                           max_date).iat[0] == pd.Timestamp('2019-03-01')
    assert cli.apply_end_d('paid', test_cases[2],
                           max_date).iat[0] == pd.Timestamp('2019-07-01')
    assert cli.apply_end_d('current', test_cases[3],
                           max_date).iat[0] == max_date
