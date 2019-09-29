#!/usr/bin/env bash

dvc run -d lendingclub/csv_preparation/04_clean_pmt_history.py \
        -d data/raw_loan_info.fth \
        -o data/clean_pmt_history.fth \
        -f run/04_clean_pmt_history.dvc \
        python lendingclub/csv_preparation/04_clean_pmt_history.py
