
import quandl
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import math
import matplotlib.pylab as pylab

def compute_histogram_bins(data, desired_bin_size):
    try:
        min_val = np.min(data)
        max_val = np.max(data)
        min_boundary = -1.0 * (min_val % desired_bin_size - min_val)
        max_boundary = max_val - max_val % desired_bin_size + desired_bin_size
        n_bins = int((max_boundary - min_boundary) / desired_bin_size) + 1
        bins = np.linspace(min_boundary, max_boundary, n_bins)
        return bins
    except:
        return none

import matplotlib.pylab as pylab
params = {'legend.fontsize': 'x-large',
          'figure.figsize': (15, 5),
         'axes.labelsize': 'x-large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'x-large',
         'ytick.labelsize':'x-large'}
pylab.rcParams.update(params)    
    
# ROUNDUP is used for x axis scaling
def roundup(x, n = 10):
    return int(math.ceil(x / n)) * n    

# USE QUANDL TO GET DATA
authToken = "H4SeCU3EqMUafd1mTNyK"
quandl_id = "MULTPL/SHILLER_PE_RATIO_MONTH"

#getting data
df = quandl.get(quandl_id, authtoken = authToken)
df = df["Value"]

# START COMPUTING SOME STATISTICS
mu = df.mean()
sigma = df.std()
rounded_max = roundup(df.max())

# import logo
logo = plt.imread('/Users/Daniel\Dropbox (Personal)/DBCPers/VUFC/Small Vortex.png')
#logo = plt.imread('https://www.dropbox.com/s/u3lj6wi0e3bvzk5/Small%20VORTEX.png?dl=0')

fig, ax = plt.subplots(figsize = (20,6))

ax.set_xlabel('CAPE LEVEL (Monthly)', fontsize="large")
ax.set_ylabel('Count', fontsize='large')
# Turn off tick labels
ax.set_yticklabels([])
x_axis_min = 0
x_axis_max = df.max()

plt.axvline(mu, color='red', linestyle='dashed', linewidth=1)
ax.figure.figimage(logo, 650, 200, alpha=.25, zorder=1)
ax = sns.distplot(df, hist_kws=dict(edgecolor="white", linewidth=2))
#axlabel = "Shiller's Monthly CAPE Ratio",
#                  label = "Monthly CAPE VALUES")

ax.legend(ncol=1, loc="upper right", frameon=True)
ax.set_title('Shiller Monthly CAPE',fontsize=16)
ax.set(xlim=(0, rounded_max + 15), ylabel="Frequency",
       xlabel="Ratio")
sns.despine(left=True, bottom=True)

plt.show()
