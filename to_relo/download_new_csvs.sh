#!/usr/bin/env bash

source <(run/configuration-parser.py --ini config.ini)

dvc run -d ${loading_housing[entry_point]} \
    -o ${loading_housing[raw_data]} \
    -f run/01-loading-housing.dvc \
    -M ${loading_housing[metric]} \
    --overwrite-dvcfile \
    python ${loading_housing[entry_point]} --round ${loading_housing[round]}
