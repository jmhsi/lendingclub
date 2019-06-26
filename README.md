# lendingclub

For data driven loan selection on lendingclub. Important packages are sklearn, pandas, numpy, pytorch, fastai.

1) Current model is RF (sklearn) + NN (pytorch). Performance was compared against picking entirely at random and picking at random within the best performing loan grade historically.
2) Investigative models are trained on old done loans and validated on newest of old done loans.
3) Models used in invest scripts are trained on all available training data.

j_utils is imported and use in several scripts. See repo https://github.com/jmhsi/j_utils

Had to chmod -R 777 latest_csvs dir?
To fix permissions troubles, I neded up adding jenkins and justin to each others groups (sudo usermod -a -G groupName userName) and allowing group rw- (read/write, no need for executeable)?
May have permission problems with all .fth or dataframes from pandas. For now, manually fixing in command line. Not sure how to best address currently.

# Notes to self:
Current jenkins setup runs in conda environment (based off https://mdyzma.github.io/2017/10/14/python-app-and-jenkins/)
Considering moving to docker containers once I build the Dockerfiles?

Made symlink: ln -s /home/justin/projects to /var/lib/jenkins/projects so jenkins can run scripts like the actual projects directory
Changed permissions of whole projects directory to get around jenkins permission errors (e.g. sudo chmod -R 777 projects)
