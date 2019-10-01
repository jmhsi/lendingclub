'''
Downloads LC csvs into dir
'''
# %load ../../lendingclub/csv_dl_archiving/01_download_LC_csvs.py
import os
import time
from shutil import copytree, rmtree

from lendingclub import config
from lendingclub.csv_dl_archiving import download_prep as dp

# setup

now = time.strftime("%m_%d_%Hh_%Mm_%Ss_%Y")
arch_name = 'raw_zipped_csvs_'+now

# make archive if it doesn't exist
os.makedirs(config.arch_dir, exist_ok=True)

# if dir for new downloads exists, delete it
if os.path.isdir(config.raw_dl_dir):
    rmtree(config.raw_dl_dir)

# download csvs
dp.download_csvs(config.raw_dl_dir)

# calculate shasum256 hash on just downloaded csvs
just_dled_hashes = dp.get_hashes(config.raw_dl_dir)


if len(os.listdir(config.arch_dir)) == 0:
    print("Archives of csvs are empty. Moving just downloaded into archives")
    copytree(config.raw_dl_dir, os.path.join(config.arch_dir, arch_name))
else:
    compare_dir = dp.get_newest_creationtime_dir(config.arch_dir)

    # check if compared to previous time, there are changes/additions/deletions in csvs
    archive_flag = dp.check_file_changes(compare_dir, just_dled_hashes)

    if archive_flag:
        print('Downloads differ from most recent archived csvs. \
              Copy to archives')
        copytree(config.raw_dl_dir, os.path.join(config.arch_dir, arch_name))
    else:
        print('Downloads do not differ from last archived. Not archiving')

print('done downloading, checking, and archiving (when necessary) the csv files!!!')



#     # if something was different (archive_flag), then store a copy of just_downloaded to archives
#     dp.archiver(archive_flag, config.csv_dir, archiver_dir = config.arch_dir)

    # # removes old downloads
    # dp.cleaner(config.csv_dir)


# # copy the downloaded files to data location
# copytree(download_dir, os.path.join(config.csv_dir, download_dir))

# # delete the original
# rmtree(download_dir)
