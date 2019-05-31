import os
import sys
import time
from shutil import copytree, rmtree
import download_prep as dp

# setup
rel_path = '../../data/csvs'
now = time.strftime("%m_%d_%Hh_%Mm_%Ss_%Y")
download_dir = 'csvs_' + now
os.mkdir(download_dir)

# download csvs
dp.download_csvs(download_dir)

# calculate shasum256 hash on just downloaded csvs
just_dled_hashes = dp.get_hashes(download_dir)

# copy the downloaded files to data location
copytree(download_dir, os.path.join(rel_path, download_dir))

# delete the original
rmtree(download_dir)

# get the dirs holding downloaded csvs by creation time (not archived_csvs dir)
csv_folders = dp.get_sorted_creationtime_dirs(rel_path)

# check if compared to previous time, there are changes/additions/deletions in csvs
archive_flag = dp.check_file_changes(csv_folders, just_dled_hashes)

# if something was different (archive_flag), then store a copy of just_downloaded to archives
dp.archiver(archive_flag, rel_path)

# removes old downloads
dp.cleaner(rel_path)

print('done downloading, checking, and archiving (when necessary) the csv files!!!')