# A temporary Readme

# lendingclub

For data driven loan selection on lendingclub. Important packages are sklearn, pandas, numpy, pytorch, fastai.

1) Current model is RF (sklearn) + NN (pytorch). Performance was compared against picking entirely at random and picking at random within the best performing loan grade historically.
2) Investigative models are trained on old done loans and validated on newest of old done loans.
3) Models used in invest scripts are trained on all available training data.

# Git Tags
Various git tags for navigating between datasets and dev/full datasets
datav0.0.0 <- model/scorer.dataprocessingtype.raw_data_csvs? Each redownload of new data, increment rightmost #?

# DVC Stuff
1) when want new raw_csvs: python lendingclub/csv_dl_archiving/01_download_LC_csvs.python
 but beware: https://dvc.org/doc/user-guide/update-tracked-file

# Usage:
Advisable to set up an environment
After cloning:
in root dir (lendingclub) with setup.py, run pip install -e .
properly setup account_info.py in user_creds (see example)

Run order (all scripts in lendingclub subdir):
1) python lendingclub/csv_dl_archiving/01_download_and_check_csvs.py
2) python lendingclub/csv_prepartion/02_unzip_csvs.py 
3) python
Before running clean_loan_info, have to cd to lendingclub/csv_preparation
python setup.py build_ext. Will make a build dir in cd, copy the .so (unix) or .pyd(windows) to cd


# Notes to self:
j_utils is imported and use in several scripts. See repo https://github.com/jmhsi/j_utils

To fix permissions troubles, I ended up adding jenkins and justin to each others groups (sudo usermod -a -G groupName userName) and doing chmod 664(774) on .fth and dataframes or other files as necessary. 

Current jenkins setup runs in conda environment (based off https://mdyzma.github.io/2017/10/14/python-app-and-jenkins/)
Considering moving to docker containers once I build the Dockerfiles?

Made symlink: ln -s /home/justin/projects to /var/lib/jenkins/projects so jenkins can run scripts like the actual projects directory

# .fth to work with after initial data and eval prep:
'eval_loan_info.fth', 'scaled_pmt_hist.fth', 'base_loan_info.fth', 'str_loan_info.fth'
