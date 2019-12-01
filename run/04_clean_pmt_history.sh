#!/usr/bin/env bash

dvc run -d lendingclub/csv_preparation/04_clean_pmt_history.py \
        -d lendingclub/csv_preparation/clean_pmt_history.py \
        -d data/csvs/02_working_csvs \
        -d data/dev_ids.pkl \
        -d data/pmt_hist_skiprows.pkl \
        -o data/clean_pmt_history.fth \
        -f run/04_clean_pmt_history.dvc \
        python lendingclub/csv_preparation/04_clean_pmt_history.py
