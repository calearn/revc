from functools import partial
from sklearn.svm import SVC
from joblib import Parallel, delayed
from scipy.stats import binomtest
from sklearn.preprocessing import MinMaxScaler

from .utils import __semitest__

import numpy as np

# reverse causality testing function
def rc_test(X, Y, base_classifier = partial(SVC, kernel = 'poly', degree = 3, coef0 = 0, probability = True), label_len = -1, job_rep = 100, normalize = False):

    if label_len == -1:
        label_len = round(X.shape[0]/10)
    
    caus = Y[:, 0] > np.median(Y[:, 0])
    effe = X[:, 1:]
    if normalize:
        effe = MinMaxScaler().fit_transform(effe)

    job_call = partial(__semitest__, base_classifier(), effe, caus, label_len)
    results = np.array(Parallel(n_jobs = job_rep, backend = "threading")(map(delayed(job_call), range(job_rep))))

    # return two p-values -- which one to use depends on the numeric precision of predictions generated by the base classifier (i.e., whether there are ties)
    return [
        binomtest(np.sum(results[:,0] < results[:,1]), np.sum(results[:,0] < results[:,1]) + np.sum(results[:,0] > results[:,1]), alternative='greater').pvalue, 
        binomtest(np.sum(results[:,0] < results[:,1]), results.shape[0], alternative='greater').pvalue
    ]