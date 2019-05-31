from fastai.imports import *
from fastai.structured import *
from fastai.column_data import *
from sklearn.base import TransformerMixin, BaseEstimator
from pandas_summary import DataFrameSummary
from sklearn.externals import joblib


class StandardScalerJustin(TransformerMixin, BaseEstimator):
    def __init__(self, copy=True, with_mean=True, with_std=True):
        self.with_mean = with_mean
        self.with_std = with_std
        self.copy = copy
    
    def fit(self, X, y=None):
        if type(X) == np.ndarray:
            X = pd.Series(X.reshape(-1))
        self.mean_ = X.dropna().mean()
        self.var_ = X.dropna().var()
        return self

    def transform(self, X):
        mean = self.mean_
        std_dev = np.sqrt(self.var_)
        if std_dev == 0:
            return X
        return (X-mean)/std_dev
    
def fit_scalers(df, mapper):
    warnings.filterwarnings('ignore', category=sklearn.exceptions.DataConversionWarning)
    if mapper is None:
        map_f = [([n],StandardScalerJustin()) for n in df.columns if is_numeric_dtype(df[n])]
        mapper = DataFrameMapper(map_f).fit(df)
    return mapper    

def proc_df_justin(df, y_fld, valid_test, skip_flds=None, do_scale=False, na_dict=None,
            preproc_fn=None, max_n_cat=None, subset=None, mapper=None, train_cols_meds=None, cols=None):

    """ proc_df takes a data frame df and splits off the response variable, and
    changes the df into an entirely numeric dataframe.

    Parameters:
    -----------
    df: The data frame you wish to process.

    y_fld: The name of the response variable
    
    valid_test: boolean indicating if this is a df to match to train columns.

    skip_flds: A list of fields that dropped from df.

    do_scale: Standardizes each column in df,Takes Boolean Values(True,False)

    na_dict: a dictionary of na columns to add. Na columns are also added if there
        are any missing values.

    preproc_fn: A function that gets applied to df.

    max_n_cat: The maximum number of categories to break into dummy values, instead
        of integer codes.

    subset: Takes a random subset of size subset from df.

    mapper: If do_scale is set as True, the mapper variable
        calculates the values used for scaling of variables during training time(mean and standard deviation).
        
    train_cols_meds: dict where keys are columns from training and values are medians, use for values to fill an entire missing column (shouldn't be needed when used to actually pick loans, was needed for train/valid/test due to new fields being added over the timeframe and missing in certain datasets while existing in others)
    
    cols: Just to compare column order and ensure the variables are in the right order.

    Returns:
    --------
    [x, y, nas, mapper(optional)]:

        x: x is the transformed version of df. x will not have the response variable
            and is entirely numeric.

        y: y is the response variable

        nas: returns a dictionary of which nas it created, and the associated median.

        mapper: A DataFrameMapper which stores the mean and standard deviation of the corresponding continous
        variables which is then used for scaling of during test-time."""        
    assert type(valid_test) == bool, print('must indiciate if this is test/valid set to match columns with train')
    
    if not skip_flds: skip_flds=[]
    if subset: df = get_sample(df,subset)
    df = df.copy()
    if preproc_fn: preproc_fn(df)
    y = df[y_fld].values
    df.drop(skip_flds+[y_fld], axis=1, inplace=True)

    # fit the scalers
    if do_scale: mapper = fit_scalers(df, mapper)
    if na_dict is None: na_dict = {}      
    for n,c in df.items(): na_dict = fix_missing(df, c, n, na_dict)
    df[mapper.transformed_names_] = mapper.transform(df)
    embeddings=[]
    for n,c in df.items():
        numericalize(df, c, n, max_n_cat)
        if not is_numeric_dtype(c):
            embeddings.append(prep_embeddings(c, n))
    df = pd.get_dummies(df, dummy_na=True)
    # fix the nas
    if valid_test:
        for col, med in train_cols_meds.items():
            try:
                df[col].fillna(med, inplace=True)
            except KeyError:
                print(col)
                df[col] = med
        df = df[cols]
        
    res = [df, y, na_dict, embeddings]
    if not valid_test: res += [res[0].median(), res[0].columns]
    if do_scale: res = res + [mapper]
    return res

def prep_embeddings(c, n):
    # allocate in embeddings for a null
    return (n, len(c.cat.categories)+1)

def eval_models(trials, port_size, available_loans, regr_version, X_test, y_test,
                default_series, yhat_test): #regr, 
    results = {}
    pct_default = {}
    test_copy = X_test.copy()
    
    default_series = default_series.loc[X_test.index]
    yhats_ys_defs = pd.DataFrame([yhat_test, y_test, default_series.values]).T
    yhats_ys_defs.rename(columns={0:'yhat', 1:'y', 2:'defaults'}, inplace=True)
    for trial in tqdm_notebook(np.arange(trials)):
        # of all test loans, grab a batch of n=available_loans
        available_idx = np.random.choice(
            np.arange(len(test_copy)), available_loans, replace=False)
        available_loans_df = yhats_ys_defs.ix[available_idx,:]
        available_loans_df.sort_values('yhat', inplace=True, ascending=False)
        picks = available_loans_df[:port_size]
        results[trial] = picks['y'].mean()
        pct_default[trial] = picks['defaults'].sum()/port_size
    pct_default_series = pd.Series(pct_default)
    results_df = pd.DataFrame(pd.Series(results))
    results_df['pct_def'] = pct_default_series
    results_df.columns = pd.MultiIndex(levels=[[regr_version], [0.07, 'pct_def']],
           labels=[[0, 0,], [0, 1,]],
           names=['discount_rate', 'model'])
    return results_df

def load_RF():
    return joblib.load(f'{PATH_RF}{regr_version_RF}_{training_type}.pkl')

def load_NN():
    with open(f'{data_save_path}/for_proc_df_model_loading.pkl', 'rb') as handle:
        nas_all_train, embeddings_all_train, train_cols_meds_all_train, cols_all_train, mean_stdev_mapper_all_train, dl_df_train, dl_ys_train, cat_vars, emb_szs = pickle.load(handle)
    val_idxs = [0]
    bs = 64
    X_test = None
    regr_version_NN = '1.0.1'
    training_type = 'all'
    md = ColumnarModelData.from_data_frame(PATH_NN, val_idxs, dl_df_train, dl_ys_train, cat_vars, bs, test_df=X_test)
    n_cont = len(dl_df_train.columns)-len(cat_vars)
    nn = md.get_learner(emb_szs, n_cont, 0.05, 1, [1000,500,500,250,250], [0.2,0.2,.2,.15,.05])
    nn.load(f'{PATH_NN}{regr_version_NN}_{training_type}.pth')
    
def add_dateparts(df):
    '''Uses the fastai add_datepart to turn datetimes into numbers to process
       does not do it for issue_d'''
    date_cols = df.select_dtypes(['datetime64']).columns
    for date_col in date_cols:
        if date_col not in special_cols:
            add_datepart(df, date_col, drop=True)
    return [col for col in date_cols if col not in special_cols]    
    
# for saving
special_cols = []
platform = 'lendingclub'
datapath = '/home/justin/all_data/'
PATH_NN = f'{datapath}{platform}/NN/'
PATH_RF = f'{datapath}{platform}/RF/'
data_save_path = f'{datapath}{platform}/'
training_type = 'all'
regr_version_RF = '0.2.2'
regr_version_NN = '1.0.1'