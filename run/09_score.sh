#!/usr/bin/env bash

dvc run -d lendingclub/modeling/09_score.py \
    -d data/base_loan_info.fth \
    -d data/eval_loan_info.fth \
#    -d modeling/ \
    -d lendingclub/modeling/models.py \
    -o data/eval_loan_info_scored.fth \
    -f run/09_score.dvc \
    python lendingclub/modeling/09_score.py -m catboost_both
