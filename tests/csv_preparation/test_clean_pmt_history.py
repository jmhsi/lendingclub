'''
Tests for clean_pmt_history.py which contains functions used in 04_clean_pmt_history.py
'''
import numpy as np
import pandas as pd
import pandas.api.types as ptypes
from lendingclub.csv_preparation import clean_pmt_history as cph


def test_detect_strange_pmt_hist():
    test_cases = [
        pd.DataFrame({
            'RECEIVED_D': {
                15049: 'APR2014'
            },
            'PERIOD_END_LSTAT': {
                15049: 'Current'
            },
            'MONTH': {
                15049: 'MAR2014'
            },
            'IssuedDate': {
                15049: 'FEB2014'
            },
            'State': {
                15049: 'VA'
            },
            'HomeOwnership': {
                15049: 'MORTGAGE'
            },
            'EarliestCREDITLine': {
                15049: 'OCT1994'
            },
            'EmploymentLength': {
                15049: '10+ years'
            },
            'grade': {
                15049: 'E'
            },
            'APPL_FICO_BAND': {
                15049: '675-679'
            },
            'Last_FICO_BAND': {
                15049: '700-704'
            },
            'VINTAGE': {
                15049: '14Q1'
            },
            'LOAN_ID': {
                15049: 12287070
            },
            'PBAL_BEG_PERIOD': {
                15049: 27600.0
            },
            'PRNCP_PAID': {
                15049: 267.510009765625
            },
            'INT_PAID': {
                15049: 471.2699890136719
            },
            'FEE_PAID': {
                15049: 0.0
            },
            'DUE_AMT': {
                15049: 738.780029296875
            },
            'RECEIVED_AMT': {
                15049: 738.780029296875
            },
            'PBAL_END_PERIOD': {
                15049: 27332.490234375
            },
            'MOB': {
                15049: 1
            },
            'CO': {
                15049: 0
            },
            'COAMT': {
                15049: 0.0
            },
            'InterestRate': {
                15049: 0.05999999865889549
            },
            'MONTHLYCONTRACTAMT': {
                15049: 614.2999877929688
            },
            'dti': {
                15049: 22.079999923706055
            },
            'MonthlyIncome': {
                15049: 6250.0
            },
            'OpenCREDITLines': {
                15049: 17.0
            },
            'TotalCREDITLines': {
                15049: 47.0
            },
            'RevolvingCREDITBalance': {
                15049: 23483
            },
            'RevolvingLineUtilization': {
                15049: 0.6909999847412109
            },
            'Inquiries6M': {
                15049: 3.0
            },
            'DQ2yrs': {
                15049: 0.0
            },
            'MonthsSinceDQ': {
                15049: np.nan
            },
            'PublicRec': {
                15049: 0.0
            },
            'MonthsSinceLastRec': {
                15049: np.nan
            },
            'currentpolicy': {
                15049: 1
            },
            'term': {
                15049: 60
            },
            'PCO_RECOVERY': {
                15049: np.nan
            },
            'PCO_COLLECTION_FEE': {
                15049: np.nan
            }
        }),
        pd.DataFrame({
            'RECEIVED_D': {
                0: 'SEP2007'
            },
            'PERIOD_END_LSTAT': {
                0: 'Current'
            },
            'MONTH': {
                0: 'SEP2007'
            },
            'IssuedDate': {
                0: 'AUG2007'
            },
            'State': {
                0: 'FL'
            },
            'HomeOwnership': {
                0: 'RENT'
            },
            'EarliestCREDITLine': {
                0: 'MAY2005'
            },
            'EmploymentLength': {
                0: '1 year'
            },
            'grade': {
                0: 'G'
            },
            'APPL_FICO_BAND': {
                0: '640-644'
            },
            'Last_FICO_BAND': {
                0: '640-644'
            },
            'VINTAGE': {
                0: '07Q3'
            },
            'LOAN_ID': {
                0: 114469
            },
            'PBAL_BEG_PERIOD': {
                0: 13000.0
            },
            'PRNCP_PAID': {
                0: 278.3390808105469
            },
            'INT_PAID': {
                0: 186.60092163085938
            },
            'FEE_PAID': {
                0: 0.0
            },
            'DUE_AMT': {
                0: 464.95001220703125
            },
            'RECEIVED_AMT': {
                0: 464.94000244140625
            },
            'PBAL_END_PERIOD': {
                0: 12721.6611328125
            },
            'MOB': {
                0: 1
            },
            'CO': {
                0: 0
            },
            'COAMT': {
                0: 0.0
            },
            'InterestRate': {
                0: 0.17219999432563782
            },
            'MONTHLYCONTRACTAMT': {
                0: 464.95001220703125
            },
            'dti': {
                0: 15.979999542236328
            },
            'MonthlyIncome': {
                0: 2666.666748046875
            },
            'OpenCREDITLines': {
                0: 6.0
            },
            'TotalCREDITLines': {
                0: 7.0
            },
            'RevolvingCREDITBalance': {
                0: 6703
            },
            'RevolvingLineUtilization': {
                0: 0.7979999780654907
            },
            'Inquiries6M': {
                0: 1.0
            },
            'DQ2yrs': {
                0: 0.0
            },
            'MonthsSinceDQ': {
                0: 0.0
            },
            'PublicRec': {
                0: 0.0
            },
            'MonthsSinceLastRec': {
                0: 0.0
            },
            'currentpolicy': {
                0: 0
            },
            'term': {
                0: 36
            },
            'PCO_RECOVERY': {
                0: np.nan
            },
            'PCO_COLLECTION_FEE': {
                0: np.nan
            }
        })
    ]
    assert cph.detect_strange_pmt_hist(test_cases[0])
    assert not cph.detect_strange_pmt_hist(test_cases[1])


def test_pmt_hist_fmt_date():
    test_cases = [
        pd.DataFrame({
            'pmt_date': {
                0: 'SEP2007'
            },
            'status_period_end': {
                0: 'Current'
            },
            'date': {
                0: 'SEP2007'
            },
            'issue_d': {
                0: 'AUG2007'
            },
            'addr_state': {
                0: 'FL'
            },
            'home_ownership': {
                0: 'RENT'
            },
            'first_credit_line': {
                0: 'MAY2005'
            },
            'emp_len': {
                0: '1 year'
            },
            'grade': {
                0: 'G'
            },
            'fico_apply': {
                0: '640-644'
            },
            'fico_last': {
                0: '640-644'
            },
            'vintage': {
                0: '07Q3'
            },
            'loan_id': {
                0: 114469
            },
            'outs_princp_beg': {
                0: 13000.0
            },
            'princp_paid': {
                0: 278.3389892578125
            },
            'int_paid': {
                0: 186.6009979248047
            },
            'fee_paid': {
                0: 0.0
            },
            'amt_due': {
                0: 464.95001220703125
            },
            'amt_paid': {
                0: 464.94000244140625
            },
            'outs_princp_end': {
                0: 12721.6611328125
            },
            'm_on_books': {
                0: 1
            },
            'charged_off_this_month': {
                0: 0
            },
            'charged_off_amt': {
                0: 0.0
            },
            'int_rate': {
                0: 0.1720000058412552
            },
            'monthly_pmt': {
                0: 464.95001220703125
            },
            'dti': {
                0: 15.979999542236328
            },
            'm_income': {
                0: 2666.6669921875
            },
            'open_credit_lines': {
                0: 6.0
            },
            'total_credit_lines': {
                0: 7.0
            },
            'revol_credit_bal': {
                0: 6703
            },
            'revol_line_util': {
                0: 0.7979999780654907
            },
            'inq_6m': {
                0: 1.0
            },
            'dq_24m': {
                0: 0.0
            },
            'm_since_dq': {
                0: 0.0
            },
            'public_recs': {
                0: 0.0
            },
            'm_since_rec': {
                0: 0.0
            },
            'current_policy': {
                0: 0
            },
            'term': {
                0: 36
            },
            'recovs': {
                0: np.nan
            },
            'recov_fees': {
                0: np.nan
            },
            'calc_amt_paid': {
                0: 464.94000244140625
            }
        })
    ]
    test_col = 'date'
    cph.pmt_hist_fmt_date(test_cases[0], test_col)
    assert ptypes.is_datetime64_any_dtype(test_cases[0][test_col])


def test_merge_dupe_dates():
    test_cases = [(pd.DataFrame({
        'pmt_date': {
            7060: pd.NaT,
            7061: pd.NaT
        },
        'status_period_end': {
            7060: 'defaulted',
            7061: 'charged_off'
        },
        'date': {
            7060: pd.Timestamp('2014-07-01 00:00:00'),
            7061: pd.Timestamp('2014-07-01 00:00:00')
        },
        'issue_d': {
            7060: pd.Timestamp('2013-03-01 00:00:00'),
            7061: pd.Timestamp('2013-03-01 00:00:00')
        },
        'addr_state': {
            7060: 'FL',
            7061: 'FL'
        },
        'home_ownership': {
            7060: 'mortgage',
            7061: 'mortgage'
        },
        'first_credit_line': {
            7060: pd.Timestamp('1999-09-01 00:00:00'),
            7061: pd.Timestamp('1999-09-01 00:00:00')
        },
        'emp_len': {
            7060: '< 1 year',
            7061: '< 1 year'
        },
        'grade': {
            7060: 'B',
            7061: 'B'
        },
        'vintage': {
            7060: '13Q1',
            7061: '13Q1'
        },
        'outs_princp_beg': {
            7060: 5649.046875,
            7061: 2000
        },
        'princp_paid': {
            7060: 5,
            7061: 0.0
        },
        'int_paid': {
            7060: 5,
            7061: 0.0
        },
        'fee_paid': {
            7060: 5,
            7061: 0.0
        },
        'amt_due': {
            7060: 1031.9599609375,
            7061: 1286.199951171875
        },
        'amt_paid': {
            7060: 15,
            7061: 0.0
        },
        'outs_princp_end': {
            7060: 5649.046875,
            7061: 5649.046875
        },
        'm_on_books': {
            7060: 15,
            7061: 16
        },
        'charged_off_this_month': {
            7060: 0,
            7061: 1
        },
        'charged_off_amt': {
            7060: 10,
            7061: 20
        },
        'int_rate': {
            7060: 0.11100000143051147,
            7061: 0.11100000143051147
        },
        'monthly_pmt': {
            7060: 254.24000549316406,
            7061: 254.24000549316406
        },
        'dti': {
            7060: 32.36000061035156,
            7061: 32.36000061035156
        },
        'm_income': {
            7060: 6066.666015625,
            7061: 6066.666015625
        },
        'open_credit_lines': {
            7060: 13.0,
            7061: 13.0
        },
        'total_credit_lines': {
            7060: 51.0,
            7061: 51.0
        },
        'revol_line_util': {
            7060: 0.6439999938011169,
            7061: 0.6439999938011169
        },
        'inq_6m': {
            7060: 3.0,
            7061: 3.0
        },
        'dq_24m': {
            7060: 0.0,
            7061: 0.0
        },
        'm_since_dq': {
            7060: 55.0,
            7061: 55.0
        },
        'public_recs': {
            7060: 0.0,
            7061: 0.0
        },
        'm_since_rec': {
            7060: np.nan,
            7061: np.nan
        },
        'current_policy': {
            7060: 1,
            7061: 1
        },
        'term': {
            7060: 36,
            7061: 36
        },
        'recovs': {
            7060: 20,
            7061: 30
        },
        'recov_fees': {
            7060: 15,
            7061: 25
        },
        'all_cash_to_inv': {
            7060: 100,
            7061: 200
        },
        'fico_apply': {
            7060: 712,
            7061: 712
        },
        'fico_last': {
            7060: 587,
            7061: 582
        },
        'loan_id': {
            7060: 3626698,
            7061: 3626698
        },
        'revol_credit_bal': {
            7060: 31549.0,
            7061: 31549.0
        }
    }), {
        'pmt_date': 0,
        'status_period_end': 1,
        'date': 2,
        'issue_d': 3,
        'addr_state': 4,
        'home_ownership': 5,
        'first_credit_line': 6,
        'emp_len': 7,
        'grade': 8,
        'vintage': 9,
        'outs_princp_beg': 10,
        'princp_paid': 11,
        'int_paid': 12,
        'fee_paid': 13,
        'amt_due': 14,
        'amt_paid': 15,
        'outs_princp_end': 16,
        'm_on_books': 17,
        'charged_off_this_month': 18,
        'charged_off_amt': 19,
        'int_rate': 20,
        'monthly_pmt': 21,
        'dti': 22,
        'm_income': 23,
        'open_credit_lines': 24,
        'total_credit_lines': 25,
        'revol_line_util': 26,
        'inq_6m': 27,
        'dq_24m': 28,
        'm_since_dq': 29,
        'public_recs': 30,
        'm_since_rec': 31,
        'current_policy': 32,
        'term': 33,
        'recovs': 34,
        'recov_fees': 35,
        'all_cash_to_inv': 36,
        'fico_apply': 37,
        'fico_last': 38,
        'loan_id': 39,
        'revol_credit_bal': 40
    })]
    ex = cph.merge_dupe_dates(*test_cases[0])
    assert ex.shape[0] == 1
    assert ex['outs_princp_beg'].iloc[0] == 5649.046875
    assert ex['princp_paid'].iloc[0] == 5
    assert ex['int_paid'].iloc[0] == 5
    assert ex['fee_paid'].iloc[0] == 5
    assert ex['amt_paid'].iloc[0] == 15
    assert ex['charged_off_this_month'].iloc[0] == 1
    assert ex['charged_off_amt'].iloc[0] == 30
    assert ex['recovs'].iloc[0] == 50
    assert ex['recov_fees'].iloc[0] == 40
    assert ex['all_cash_to_inv'].iloc[0] == 300
    
def test_insert_missing_dates():
    test_cases = [
        (pd.DataFrame(
            {'pmt_date': {7059: pd.NaT, 7061: pd.NaT},
             'status_period_end': {7059: 'late_120', 7061: 'charged_off'},
             'date': {7059: pd.Timestamp('2014-05-01 00:00:00'),
              7061: pd.Timestamp('2014-07-01 00:00:00')},
             'issue_d': {7059: pd.Timestamp('2013-03-01 00:00:00'),
              7061: pd.Timestamp('2013-03-01 00:00:00')},
             'addr_state': {7059: 'FL', 7061: 'FL'},
             'home_ownership': {7059: 'mortgage', 7061: 'mortgage'},
             'first_credit_line': {7059: pd.Timestamp('1999-09-01 00:00:00'),
              7061: pd.Timestamp('1999-09-01 00:00:00')},
             'emp_len': {7059: '< 1 year', 7061: '< 1 year'},
             'grade': {7059: 'B', 7061: 'B'},
             'vintage': {7059: '13Q1', 7061: '13Q1'},
             'outs_princp_beg': {7059: 5649.046875, 7061: 5649.046875},
             'princp_paid': {7059: 0.0, 7061: 0.0},
             'int_paid': {7059: 0.0, 7061: 0.0},
             'fee_paid': {7059: 0.0, 7061: 0.0},
             'amt_due': {7059: 777.719970703125, 7061: 1286.199951171875},
             'amt_paid': {7059: 0.0, 7061: 0.0},
             'outs_princp_end': {7059: 5649.046875, 7061: 5649.046875},
             'm_on_books': {7059: 14, 7061: 16},
             'charged_off_this_month': {7059: 0.0, 7061: 1.0},
             'charged_off_amt': {7059: 0.0, 7061: 5649.046875},
             'int_rate': {7059: 0.11100000143051147, 7061: 0.11100000143051147},
             'monthly_pmt': {7059: 254.24000549316406, 7061: 254.24000549316406},
             'dti': {7059: 32.36000061035156, 7061: 32.36000061035156},
             'm_income': {7059: 6066.666015625, 7061: 6066.666015625},
             'open_credit_lines': {7059: 13.0, 7061: 13.0},
             'total_credit_lines': {7059: 51.0, 7061: 51.0},
             'revol_line_util': {7059: 0.6439999938011169, 7061: 0.6439999938011169},
             'inq_6m': {7059: 3.0, 7061: 3.0},
             'dq_24m': {7059: 0.0, 7061: 0.0},
             'm_since_dq': {7059: 55.0, 7061: 55.0},
             'public_recs': {7059: 0.0, 7061: 0.0},
             'm_since_rec': {7059: np.nan, 7061: np.nan},
             'current_policy': {7059: 1, 7061: 1},
             'term': {7059: 36, 7061: 36},
             'recovs': {7059: 0.0, 7061: 786.4600219726562},
             'recov_fees': {7059: 0.0, 7061: 7.861999988555908},
             'all_cash_to_inv': {7059: 0.0, 7061: 778.5980224609375},
             'fico_apply': {7059: 712, 7061: 712},
             'fico_last': {7059: 587, 7061: 582},
             'loan_id': {7059: 3626698, 7061: 3626698},
             'revol_credit_bal': {7059: 31549.0, 7061: 31549.0}}), 3626698)
    ]

    ex = cph.insert_missing_dates(*test_cases[0], verbose=True)
    assert ex.shape[0] == 3
