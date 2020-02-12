'''
Temporary until pandas gets some kind of upsert functionality
'''
from sqlalchemy import create_engine
from lendingclub import config
import pandas as pd

# read, sort, drop
disk_engine = create_engine(f'sqlite:///{config.lc_api_db}')
df = pd.read_sql('lc_api_loans', disk_engine)
df = df.sort_values(['id', 'funded_amount'])
df = df.drop_duplicates('id', keep='last')
# df = df.drop(['index', 'level_0'], axis=1)
    

# write out
df.to_sql('lc_api_loans', disk_engine, if_exists='replace', index=False)
