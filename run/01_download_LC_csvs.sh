#!/usr/bin/env bash

dvc run -d lendingclub/csv_dl_archiving/01_download_LC_csvs.py \
        -d lendingclub/csv_dl_archiving/download_prep.py \
        -o data/csvs/raw_zipped_csvs/ \
        -o data/csvs/archived_csvs/ \
        -f run/01_download_LC_csvs.dvc \
        python lendingclub/csv_dl_archiving/01_download_LC_csvs.py

