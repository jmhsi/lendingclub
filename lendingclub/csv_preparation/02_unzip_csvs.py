'''
for unzipping the newly downloaded csvs
'''
import logging
import pathlib
import subprocess
from lendingclub import config
import os
import shutil

latest_csvs = config.wrk_csv_dir
raw_dl_csvs = config.raw_dl_dir
# if wrd_dir exists, delete to make anew
if os.path.exists(latest_csvs):
    print(f'deleting existing {latest_csvs} folder')
    shutil.rmtree(latest_csvs)
os.makedirs(latest_csvs)
print(f'extracting zips from {raw_dl_csvs} to {latest_csvs} \n')

zip_files = pathlib.Path(raw_dl_csvs).rglob("*.zip")

while True:
    try:
        path = next(zip_files)
    except StopIteration:
        break  # no more files
    except PermissionError:
        logging.exception("permission error")
    else:
        extract_dir = pathlib.Path(latest_csvs)
        subprocess.call(['unzip', '-o', path, '-d', extract_dir])

# as of 1/15/2020, unzipping the pmt_hist.zip becomes a .gz.
# Should check latest_csvs and try to unzip any file not ending in
# .csvs
gz_files = pathlib.Path(latest_csvs).rglob("*.gz")

while True:
    try:
        path = next(gz_files)
    except StopIteration:
        break  # no more files
    except PermissionError:
        logging.exception("permission error")
    else:
        extract_dir = pathlib.Path(latest_csvs)
        print(f'extracting .gz file {path}')
        subprocess.call(['gunzip', path])

print('all zip files have been unzipped')
