#!/usr/bin/env bash

dvc run -d lendingclub/csv_preparation/02_unzip_csvs.py \
        -d data/csvs/raw_zipped_csvs \
        -o data/csvs/02_working_csvs \
        -f run/02_unzip_csvs.dvc \
        python lendingclub/csv_preparation/02_unzip_csvs.py 
