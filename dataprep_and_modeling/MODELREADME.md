model versions are of form '#.#.#'. 1st number is when big changes to imputation methods occur. 2nd number is when underlying algorithim/model changes e.g. from elastic net to random forest/neuralnet. 3rd number is for changes in tuning/hyperparams/layers.

In the lending club store are two dataframes relevant form model comparisons. 'model_info' has details of the models and 'results' hold the trials from the models. Best to use results.describe() to get quick summaries. 

TODO: Eventually should also check percentiles within a certain model, and store that information as well.
