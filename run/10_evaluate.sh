#!/usr/bin/env bash

dvc run -d lendingclub/modeling/10_evaluate.py \
    -d data/eval_loan_info_scored.fth \
    -m results/default_rate.json \
    -m results/return.json \
    -m results/mbm_return.json \
    -m results/mbm_default_rate.json \
    -f run/10_evaluate.dvc \
    python lendingclub/modeling/10_evaluate.py 
