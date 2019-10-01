'''
for unzipping the newly downloaded csvs
'''
# %load ../../lendingclub/csv_preparation/02_unzip_csvs.py
import logging
import pathlib
import subprocess
from lendingclub import config
# sys.path.append(os.path.join(os.path.expanduser('~'), 'projects'))
# sys.path.append(os.path.join(os.path.expanduser('~'), 'projects', 'lendingclub'))
# import lendingclub.scripts.csv_dl_archiving.download_prep as dp

latest_csvs = config.wrk_csv_dir
# if os.path.exists(latest_csvs):
#     shutil.rmtree(latest_csvs)
# os.makedirs(latest_csvs)
zip_files = pathlib.Path(config.raw_dl_dir).rglob("*.zip")

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
# for root, dirs, files in os.walk(latest_csvs):
#     for d in dirs:
#         os.chmod(os.path.join(root, d), 0o777)
#     for f in files:
#         os.chmod(os.path.join(root, f), 0o777)
