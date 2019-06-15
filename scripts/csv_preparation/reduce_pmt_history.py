from tqdm import tqdm
import os
import sys
import pandas as pd

csv_path = os.path.join(os.path.expanduser('~'), 'projects', 'lendingclub', 'data', 'csvs', 'latest_csvs')
# for now its always been one csv. Will have to revisit if they break it out to multiple
pmt_hist_fnames = [f for f in os.listdir(csv_path) if 'PMTHIST' in f]
pmt_hist_path = os.path.join(csv_path, pmt_hist_fnames[0])
pmt_hist = pd.read_csv(pmt_hist_path, low_memory=False)
print("{:,}".format(len(pmt_hist)) + " rows of pmt_hist loaded")

# compress memory
sys.path.append(os.path.join(os.path.expanduser('~'), 'projects'))
import j_utils.munging as mg
changed_type_cols, pmt_hist = mg.reduce_memory(pmt_hist)

# save
dpath = os.path.join(os.path.expanduser('~'), 'projects', 'lendingclub', 'data')
pmt_hist.to_feather(os.path.join(dpath, 'raw_pmt_hist_1.fth'))
