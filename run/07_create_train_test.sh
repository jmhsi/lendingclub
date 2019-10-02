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
    -o data/test_eval_loan_info_0_bootstrap.fth \
    -o data/test_eval_loan_info_1_bootstrap.fth \
    -o data/test_eval_loan_info_2_bootstrap.fth \
    -o data/test_eval_loan_info_3_bootstrap.fth \
    -o data/test_eval_loan_info_4_bootstrap.fth \
    -o data/test_eval_loan_info_5_bootstrap.fth \
    -o data/test_eval_loan_info_6_bootstrap.fth \
    -o data/test_eval_loan_info_7_bootstrap.fth \
    -o data/test_eval_loan_info_8_bootstrap.fth \
    -o data/test_eval_loan_info_9_bootstrap.fth \
    -f run/07_create_train_test.dvc \
    python lendingclub/data_and_eval_preparation/07_create_train_test.py 
