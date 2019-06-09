import os
import logging
import pathlib
import shutil
import subprocess
import lendingclub.scripts.csv_dl_archiving.download_prep as dp

dpath = '/home/justin/projects/lendingclub/data/csvs'
working_csvs = os.path.join(dpath, 'latest_csvs')
if os.path.exists(working_csvs):
    shutil.rmtree(working_csvs)
os.makedirs(working_csvs)
csv_path = dp.get_sorted_creationtime_dirs(dpath)[-1][1]
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
        extract_dir = pathlib.Path(working_csvs)
        subprocess.call(['unzip', '-o', path, '-d', extract_dir])
