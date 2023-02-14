from __future__ import print_function
import numpy as np
from scipy.stats import ttest_ind, ttest_ind_from_stats, ks_2samp, mannwhitneyu, wilcoxon
from scipy.special import stdtr
import sys
import time
import pandas as pd
import matplotlib.pyplot as plt
from numpy import genfromtxt
import argparse
from pathlib import Path

parser = argparse.ArgumentParser()

parser.add_argument("sample1")
parser.add_argument("sample2")
parser.add_argument("statsTest")
parser.add_argument("format")

args = parser.parse_args()

#if len(args) < 4:
#^TypeError, parse_args() returns a namespace, but doesn't depopulate sys.argv[]. Using that instead.
if len(sys.argv) < 4:
    print("usage: python statsTest.py sample1 sample2 (t-test,ks-test,mannwhitneyu,wilcoxon) (line-seperated,csv)")
else:
    arg1 = args.sample1
    arg2 = args.sample2
    whattest = args.statsTest
    format = args.format



if format == "csv":
	a = pd.read_csv(arg1, skiprows=2, usecols=['Latency (difference)'])
	b = pd.read_csv(arg2, skiprows=2, usecols=['Latency (difference)'])
elif format == "line-seperated":
	#deals with line or space seperated numbers
	a = np.genfromtxt(sys.argv[1])
	b = np.genfromtxt(sys.argv[2])
#	print(a)#
#	print("B:")
#	print(b)

else:
    print("format is invalid. Specified format:" + format)

if whattest == "t-test":
    t, p = ttest_ind(a, b, equal_var=False)
    print("t-test: t= %g\np=%g" % (t,p))
elif whattest == "ks-test":
    x = ks_2samp(a, b)
    print(x)
elif whattest == "mannwhitneyu":
    x = mannwhitneyu(a, b, nan_policy='raise')
    print(x)
elif whattest == "wilcoxon":
    x = wilcoxon(a, b, nan_policy='raise')
    print(x)
else:
    print("invalid test type\n")
    print("usage: python statsTest.py sample1 sample2 (t-test,ks-test,mannwhitneyu,wilcoxon) (line-seperated,csv)")

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
