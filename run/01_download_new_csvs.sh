#!/usr/bin/env bash

# source <(run/configuration-parser.py --ini config.ini)
# echo $PWD
# cd ../lendingclub/csv_dl_archiving
# echo $PWD
# dvc run -d ${downloading_LC_csvs[entry_point]} \
#         -o ${downloading_LC_csvs[datadir_out]} \
#         -f run/01_downloading_LC_csvs.dvc \
# #        -M ${loading_housing[metric]} \
#         --overwrite-dvcfile \
#         python ${downlading_LC_csvs[entry_point]}

dvc run -d lendingclub/csv_dl_archiving/01_download_and_check_csvs.py \
        -o data/csvs/02_working_csvs \
        -f run/01_downloading_LC_csvs.dvc \
        --overwrite-dvcfile \
        python lendingclub/csv_dl_archiving/01_download_and_check_csvs.py

