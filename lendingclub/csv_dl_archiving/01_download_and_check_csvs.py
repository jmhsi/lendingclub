import os
import sys
import time
from shutil import copytree, rmtree
import download_prep as dp
from lendingclub import config

# print(dp.__file__)
# print(sys.path)
# print(config.src_dir)

# setup
# config.csv_dir = '../../data/csvs'
now = time.strftime("%m_%d_%Hh_%Mm_%Ss_%Y")
download_dir = 'csvs_' + now
os.mkdir(download_dir)

# download csvs
dp.download_csvs(download_dir)

# calculate shasum256 hash on just downloaded csvs
just_dled_hashes = dp.get_hashes(download_dir)

# copy the downloaded files to data location
copytree(download_dir, os.path.join(config.csv_dir, download_dir))

# delete the original
rmtree(download_dir)

# get the dirs holding downloaded csvs by creation time (not archived_csvs dir)
csv_folders = dp.get_sorted_creationtime_dirs(config.csv_dir)

# check if compared to previous time, there are changes/additions/deletions in csvs
archive_flag = dp.check_file_changes(csv_folders, just_dled_hashes)

# if something was different (archive_flag), then store a copy of just_downloaded to archives
dp.archiver(archive_flag, config.csv_dir, archiver_dir = config.arch_dir)

# removes old downloads
dp.cleaner(config.csv_dir)

print('done downloading, checking, and archiving (when necessary) the csv files!!!')
