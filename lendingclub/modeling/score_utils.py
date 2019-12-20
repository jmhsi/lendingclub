'''
Some utility functions for combining scores for catboost clf and regr
constants updated on 2019-12-09 21:30:04 
'''

min_comb_29_score = 0.8292615853334968 #this version based off test_scores only
# min_comb_29_score = 0.825562573351525 #this version based off all_scores

def scale_cb_regr_score(df):
    '''
    returns scaled score catboost_regr_scl. scaled to max/min of all historical
    predictions (all known loans, not just done, at time of model creation which as of 12.9.2019)
    is around 2.6 million loans.)
    '''
    cb_regr_min = -1.0514865667720885
    cb_regr_max = 0.3253468660329166
    return (df['catboost_regr'] - cb_regr_min)/(cb_regr_max - cb_regr_min)

def combined_score(clf_wt):
    '''
    returns a function that makes a linear combination of scores with passed
    clf_wt for the classifier
    '''
    def lin_comb_clf_regr(clf_score, regr_score, df):
        '''
        given colnames for clf and regr, makes a linear combination of 
        the scores
        '''
        return df[clf_score]*clf_wt + (1-clf_wt)*df[regr_score]
    return lin_comb_clf_regr
