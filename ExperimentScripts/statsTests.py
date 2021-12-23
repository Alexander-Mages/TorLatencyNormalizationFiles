from __future__ import print_function
import numpy as np
from scipy.stats import ttest_ind, ttest_ind_from_stats, ks_2samp, mannwhitneyu
from scipy.special import stdtr
import sys
import time
import pandas as pd
import matplotlib.pyplot as plt
from numpy import genfromtxt

arg1 = sys.argv[1]
arg2 = sys.argv[2]
whattest = sys.argv[3]

if not arg1 or not arg2 or not whattest:
    print("usage: t-test.py sample1.csv sample2.csv test-type(t-test/ks-test/mannwhitneyu)")

a = pd.read_csv(arg1, skiprows=2, usecols=['Latency (difference)'])
b = pd.read_csv(arg2, skiprows=2, usecols=['Latency (difference)'])

#deals with line or space seperated numbers
#a = np.genfromtxt(sys.argv[1])
#b = np.genfromtxt(sys.argv[2])

if whattest == "t-test":
    t, p = ttest_ind(a, b, equal_var=False)
    print("t-test: t= %g\np=%g" % (t,p))
elif whattest == "ks-test":
    x = ks_2samp(a, b)
    print(x)
elif whattest == "mannwhitneyu":
    x = mannwhitneyu(a, b)
    print(x)
else:
    print("invalid test type\nusage: t-test.py sample1.csv sample2.csv test-type(t-test/ks-test)")




# plt.style.use('seaborn-deep')
#
#
#
# bins = np.linspace(-10, 10, 30)
#
# plt.hist([a, b], bins, label=['x', 'y'])
# plt.legend(loc='upper right')
# plt.show()

#colors = ['b','g']

#plots the histogram
#fig, ax1 = plt.subplots()
#ax1.hist([a,b],color=colors)
#ax1.set_xlim(-3,3)
#ax1.set_ylabel("Count")
#plt.tight_layout()
#plt.show()

# #
# bins = np.linspace(0, 1, 100)
# pyplot.hist(a, bins, alpha=0.25, label='x')
# pyplot.hist(b, bins, alpha=0.25, label='y')
# pyplot.legend(loc='upper right')
# pyplot.show()

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
