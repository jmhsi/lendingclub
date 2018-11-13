import pandas as pd

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