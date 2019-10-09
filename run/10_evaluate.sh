#!/usr/bin/env bash

dvc run -d lendingclub/modeling/10_evaluate.py \
    -d data/eval_loan_info_scored.fth \
    -o results/ \
    -f run/10_evaluate.dvc \
    python lendingclub/modeling/10_evaluate.py 
