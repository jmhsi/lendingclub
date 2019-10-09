#!/usr/bin/env bash

dvc run -d lendingclub/data_and_eval_preparation/07_create_train_test.py \
    -d data/base_loan_info.fth \
    -d data/scaled_pmt_hist.fth \
    -d data/eval_loan_info.fth \
    -o data/train_testable_eval_loan_info.fth \
    -o data/train_testable_base_loan_info.fth \
    -o data/test_eval_loan_info.fth \
    -o data/train_eval_loan_info.fth \
    -o data/test_base_loan_info.fth \
    -o data/train_base_loan_info.fth \
    -o data/bootstrap_test_eval_loan_info_ids.pkl \
    -f run/07_create_train_test.dvc \
    python lendingclub/data_and_eval_preparation/07_create_train_test.py 
