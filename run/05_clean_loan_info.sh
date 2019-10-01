#!/usr/bin/env bash

dvc run -d lendingclub/csv_preparation/05_clean_loan_info.py \
        -d data/raw_loan_info.fth \
        -d data/clean_pmt_history.fth \
        -o data/clean_loan_info.fth \
        -o data/strings_loan_info.fth \
        -f run/05_clean_loan_info.dvc \
        python lendingclub/csv_preparation/05_clean_loan_info.py 
