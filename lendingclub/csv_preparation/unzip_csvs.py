import os
import sys
import logging
import pathlib
import shutil
import subprocess
from lendingclub.csv_dl_archiving import download_prep as dp
from lendingclub import config
# sys.path.append(os.path.join(os.path.expanduser('~'), 'projects'))
# sys.path.append(os.path.join(os.path.expanduser('~'), 'projects', 'lendingclub'))
# import lendingclub.scripts.csv_dl_archiving.download_prep as dp

latest_csvs = config.wrk_csv_dir
if os.path.exists(latest_csvs):
    shutil.rmtree(latest_csvs)
os.makedirs(latest_csvs)
csv_path = dp.get_sorted_creationtime_dirs(config.arch_dir)[-1][1] # get last, path portion of tuple
zip_files = pathlib.Path(csv_path).rglob("*.zip")

while True:
    try:
        path = next(zip_files)
    except StopIteration:
        print('all zip files have been unzipped')
        break  # no more files
    except PermissionError:
        logging.exception("permission error")
    else:
        extract_dir = pathlib.Path(latest_csvs)
        subprocess.call(['unzip', '-o', path, '-d', extract_dir])
        
for root, dirs, files in os.walk(latest_csvs):
    for d in dirs:
        os.chmod(os.path.join(root, d), 0o777)
    for f in files:
        os.chmod(os.path.join(root, f), 0o777)
