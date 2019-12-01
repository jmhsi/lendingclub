#!/usr/bin/env bash

dvc run -d lendingclub/data_and_eval_preparation/07_create_train_test.py \
    -d data/strange_pmt_hist_ids.pkl \
    -d data/base_loan_info.fth \
    -d data/eval_loan_info.fth \
    -o data/train_test_ids.pkl \
    -o data/bootstrap_test_idx.pkl \
    -f run/07_create_train_test.dvc \
    python lendingclub/data_and_eval_preparation/07_create_train_test.py 
