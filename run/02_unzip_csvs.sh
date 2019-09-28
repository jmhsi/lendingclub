#!/usr/bin/env bash

dvc run -d lendingclub/csv_preparation/02_unzip_csvs.py \
    -o data/csvs/02_working_csvs \
    -f run/02_unzip_csvs.dvc \
    #        --overwrite-dvcfile \
    python lendingclub/csv_preparation/02_unzip_csvs.py

