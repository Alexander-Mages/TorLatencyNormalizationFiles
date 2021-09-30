from __future__ import print_function
import numpy as np
from scipy.stats import ttest_ind, ttest_ind_from_stats, ks_2samp, mannwhitneyu
from scipy.special import stdtr
import sys
import time
import csv
arg1 = sys.argv[1]
arg2 = sys.argv[2]
ksorttest = sys.argv[3]

if not arg1 or not arg2 or not ksorttest:
    print("usage: t-test.py sample1.csv sample2.csv test-type(t-test/ks-test/mannwhitneyu)")

#by default deals with line or space seperated numbers
a = np.genfromtxt(sys.argv[1])
b = np.genfromtxt(sys.argv[2])

if ksorttest == "t-test":
    t, p = ttest_ind(a, b, equal_var=False)
    print("t-test: t= %g\np=%g" % (t,p))
elif ksorttest == "ks-test":
    #kstest
    x = ks_2samp(a, b)
    print(x)
elif ksorttest == "mannwhitneyu":
    x = mannwhitneyu(a, b)
    print(x)
else:
    print("invalid test type\nusage: t-test.py sample1.csv sample2.csv test-type(t-test/ks-test)")

# abar = a.mean()
# avar = a.var(ddof=1)
# na = a.size()
# adof = na -1
#
# bbar = b.mean()
# bvar = b.var(ddof=1)
# nb = b.size
# bdof = nb -1
#^computes statistics about data
