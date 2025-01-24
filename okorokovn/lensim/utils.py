import numpy as np

from scipy.interpolate import interp1d
from scipy.optimize import brentq

microsec = 1e-6
Gbps = 1e9
Byte = 8
kB = 8e3


def jain(rates):
    return np.sum(rates) ** 2 / (len(rates) * np.sum(rates**2))


def tail(rtts, p=0.99):
    h, bins = np.histogram(rtts, bins=100)
    cdf = np.cumsum(np.concatenate(([0], h))) / len(rtts)
    cdf_tail = interp1d(bins, cdf - p)
    result = brentq(cdf_tail, bins[0], bins[-1])

    return result
