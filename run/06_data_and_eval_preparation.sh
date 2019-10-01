#!/usr/bin/env bash

dvc run -d lendingclub/data_and_eval_preparation/06_data_and_eval_preparation.py \
    -d data/clean_loan_info.fth \
    -d data/clean_pmt_history.fth \
    -d data/strings_loan_info.fth \
    -o data/clean_loan_info_api_name_matched.fth \
    -o data/base_loan_info.fth \
    -o data/scaled_pmt_hist.fth \
    -o data/eval_loan_info.fth \
    -f run/06_data_and_eval_preparation.dvc \
    python lendingclub/data_and_eval_preparation/06_data_and_eval_preparation.py 
