#!/usr/bin/env bash

dvc run -d lendingclub/modeling/08_train.py \
    -d data/train_test_ids.pkl \
    -d data/base_loan_info.fth \
    -d data/eval_loan_info.fth \
    -o modeling/ \
    -f run/08_train.dvc \
    python lendingclub/modeling/08_train.py -m catboost_regr 
