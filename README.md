# lendingclub

Go to https://jmhsi.wordpress.com for a very informal discussion about various jupyter notebooks in the repo. Posts are tagged by directory structure if you're looking for something specific.

For data driven loan selection on lendingclub. Important packages are sklearn, pandas, numpy, pytorch, fastai.

1) Current model is RF (sklearn) + NN (pytorch). Performance was compared against picking entirely at random and picking at random within the best performing loan grade historically.
2) Investigative models are trained on old done loans and validated on newest of old done loans.
3) Models used in invest scripts are trained on all available training data.
