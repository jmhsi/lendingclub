# lendingclub

For data driven loan selection on lendingclub. Important packages are sklearn, pandas, numpy, pytorch, fastai.

1) Current model is RF (sklearn) + NN (pytorch). Performance was compared against picking entirely at random and picking at random within the best performing loan grade historically.
2) Investigative models are trained on old done loans and validated on newest of old done loans.
3) Models used in invest scripts are trained on all available training data.

# Notes to self:
Current jenkins setup runs in conda environment (based off https://mdyzma.github.io/2017/10/14/python-app-and-jenkins/)
Considering moving to docker containers once I build the Dockerfiles?

for csv_dl_archiving:
used a symlink to point to the right path to download and compare csvs: ln -s /home/justin/projects/lendingclub/data/csvs /var/lib/jenkins/projects/lendingclub/data/csvs
had to change permissions to the whole data folder to allow jenkins job to copy downloaded csvs into the tree path (e.g. chmod -R data)

for csv_preparation:
