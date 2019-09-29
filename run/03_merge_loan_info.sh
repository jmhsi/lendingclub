#!/usr/bin/env bash

dvc run -d lendingclub/csv_preparation/03_merge_loan_info.py \
        -d data/csvs/02_working_csvs \
        -o data/raw_loan_info.fth \
        -f run/03_merge_loan_info.dvc \
        python lendingclub/csv_preparation/03_merge_loan_info.py 
