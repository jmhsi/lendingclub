import os
import time
import lendingclub.csv_dl_preparation.download_prep as dp

ppath = '/home/justin/all_data/lendingclub/csvs'
now = time.strftime("%Y_%m_%d_%Hh_%Mm_%Ss")
download_path = ppath + '/csvs_' + now
os.mkdir(download_path)

# download csvs
dp.download_csvs(download_path)

# calculate shasum256 hash on just downloaded csvs
just_dled_hashes = dp.get_hashes(download_path)

# get the dirs holding downlaoded csvs by creation time (not archived_csvs dir)
csv_folders = dp.get_sorted_creationtime_dirs(ppath)

# check if compared to previous time, there are changes/additions/deletions in csvs
archive_flag = dp.check_file_changes(csv_folders, just_dled_hashes)

# if something was different (archive_flag), then store a copy of just_downloaded to archives
dp.archiver(archive_flag, ppath)

# removes old downloads
dp.cleaner(ppath)

print('done downloading, checking, and archiving (when necessary) the csv files!!!')