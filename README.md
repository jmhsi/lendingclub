# A temporary Readme

# lendingclub

For data driven loan selection on lendingclub. Important packages are sklearn, pandas, numpy, pytorch, fastai.

1) Current model is RF (sklearn) + NN (pytorch). Performance was compared against picking entirely at random and picking at random within the best performing loan grade historically.
2) Investigative models are trained on old done loans and validated on newest of old done loans.
3) Models used in invest scripts are trained on all available training data.

# Usage:
Advisable to set up an environment
After cloning:
in root dir (lendingclub) with setup.py, run pip install -e .

# Notes to self:
j_utils is imported and use in several scripts. See repo https://github.com/jmhsi/j_utils

To fix permissions troubles, I ended up adding jenkins and justin to each others groups (sudo usermod -a -G groupName userName) and doing chmod 664(774) on .fth and dataframes or other files as necessary. 

Current jenkins setup runs in conda environment (based off https://mdyzma.github.io/2017/10/14/python-app-and-jenkins/)
Considering moving to docker containers once I build the Dockerfiles?

Made symlink: ln -s /home/justin/projects to /var/lib/jenkins/projects so jenkins can run scripts like the actual projects directory

# .fth to work with after initial data and eval prep:
'eval_loan_info.fth', 'scaled_pmt_hist.fth', 'base_loan_info.fth', 'str_loan_info.fth'
