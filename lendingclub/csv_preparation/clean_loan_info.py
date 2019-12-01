import pandas as pd
import numpy as np

def loan_info_fmt_date(df, col):
    month_dict = {
        'jan': '1',
        'feb': '2',
        'mar': '3',
        'apr': '4',
        'may': '5',
        'jun': '6',
        'jul': '7',
        'aug': '8',
        'sep': '9',
        'oct': '10',
        'nov': '11',
        'dec': '12'
    }

    df[col] = df[col].str.strip().str.lower()
    df[col] = pd.to_datetime(
        df[col].str[:3].replace(month_dict) +
        df[col].str[3:],
        format='%m-%Y')

def apply_end_d(status, group, max_date):
    '''
    based on last known payment from loan_info, figure out end_d based on
    status
    '''
    if status == 'charged_off':
        #split the group into two groups, one which has paid something,
        #and other which has paid nothing
        never_paid = group[group['last_pymnt_d'].isnull()]
        has_paid = group[group['last_pymnt_d'].notnull()]

        # 4 months of late (1-120) and then 1 month of chargeoff, so 5 months
        never_paid['end_d'] = never_paid['issue_d'] + pd.DateOffset(months=+5)
        has_paid['end_d'] = has_paid['last_pymnt_d'] + pd.DateOffset(months=+5)

        group.loc[never_paid.index.values, 'end_d'] = never_paid['end_d']
        group.loc[has_paid.index.values, 'end_d'] = has_paid['end_d']
        return group['end_d']
    elif status == 'paid':
        return group['last_pymnt_d']
    return pd.Series([max_date] * len(group), index=group.index.values)
