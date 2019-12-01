import pandas as pd

def check_sample_distribution(df, sample, diff_thrsh=.05, check_cols=[], verbose=True):
    '''
    check if the distribution of the sample's col and df's col is sufficiently
    close. Default tolerance is 1% difference
    '''
    if not check_cols:
        check_cols = df.columns
    pop_n = len(df)
    s_n = len(sample)
    sample_miss = {}
    big_pct_diff = {}
    for col in check_cols:
        pop_group = df[col].value_counts(dropna=False)/pop_n
        s_group = sample[col].value_counts(dropna=False)/s_n
        temp_miss = {}
        temp_diff = {}
        for k in pop_group.keys():
            if k not in s_group.keys():
                if verbose:
                    print('{0} group for {2} column is missing entirely from the sample while population has {1}'.format(k, pop_group[k], col))
                temp_miss[k] = pop_group[k]
            else:
                pct_diff = abs(pop_group[k] - s_group[k])/pop_group[k]
                if pct_diff > diff_thrsh:
                    temp_diff[k] = pct_diff
        if temp_miss:
            sample_miss[col] = temp_miss
        if temp_diff:
            big_pct_diff[col] = temp_diff
    if sample_miss or big_pct_diff:
        print("There is a sampling concern")

def check_not_same_loans(tr, te):
    return bool(len(set(tr['id']).intersection(set(te['id']))) == 0)

def check_all_loans_accounted(tr, te, to):
    return bool(tr.shape[0] + te.shape[0] == to.shape[0])

def check_same_n_instances(df1, df2):
    return bool(df1.shape[0] == df2.shape[0])

def check_same_n_cols(df1, df2):
    return bool(df1.shape[1] == df2.shape[1])

def check_train_test_testable(train, test, testable, train1, test1, testable1):
    '''
    First set for loan_info, second set for eval_loan_info
    '''
    print(train.shape, test.shape, testable.shape, train1.shape, test1.shape, testable1.shape)
    assert check_not_same_loans(train, test)
    assert check_all_loans_accounted(train, test, testable)
    assert check_not_same_loans(train1, test1)
    assert check_all_loans_accounted(train1, test1, testable1)
    assert check_same_n_instances(train, train1)
    assert check_same_n_instances(test, test1)
    assert check_same_n_instances(testable, testable1)
    assert check_same_n_cols(train, test)
    assert check_same_n_cols(train1, test1)
    return True
