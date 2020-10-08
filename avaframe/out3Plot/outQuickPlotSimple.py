"""

This is a simple function for a quick plot of datasets and option for comparison
between two datasets of identical shape. Also plots cross and longprofiles.

This file is part of Avaframe.

"""

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from avaframe.in3Utils import fileHandlerUtils as fU
import numpy as np
import os
import logging
import shutil
import glob

# Local imports
import avaframe.in3Utils.ascUtils as IOf
from avaframe.out3Plot.plotUtils import *

# create local logger
# change log level in calling module to DEBUG to see log messages
log = logging.getLogger(__name__)


def quickPlotSimple(avaDir, inputDir):
    """ Plot two raster datasets of identical dimension:

        Inputs:

        avaDir          avalanche directory
        inputDir        where input data can be found

        Outputs:

        figure 1: plot raster data for dataset1, dataset2 and their difference
        figure 2: plot cross and longprofiles for both datasets (ny_loc and nx_loc define location of profiles)
        -plots are saved to Outputs/out3SimpPlot
    """

    outDir = os.path.join(avaDir, 'Outputs', 'out3Plot')
    fU.makeADir(outDir)

    # Get name of Avalanche
    avaName = os.path.basename(avaDir)

    # Load input datasets from input directory
    datafiles = glob.glob(inputDir+os.sep + '*.asc')
    datafiles.extend(glob.glob(inputDir+os.sep + '*.txt'))

    name1 = os.path.basename(datafiles[0])
    name2 = os.path.basename(datafiles[1])
    log.info('input dataset #1 is %s' % name1)
    log.info('input dataset #2 is %s' % name2)

    # Load data
    data1 = np.loadtxt(datafiles[0], skiprows=6)
    data2 = np.loadtxt(datafiles[1], skiprows=6)
    ny = data1.shape[0]
    nx = data1.shape[1]
    header = IOf.readASCheader(datafiles[0])
    cellSize = header.cellsize
    Ly = ny*cellSize
    Lx = nx*cellSize

    # Location of Profiles
    ny_loc = int(nx * 0.5)
    nx_loc = int(ny * 0.5)

    # Difference between datasets
    dataDiff = data1 - data2
    diffMax = np.amax(dataDiff)
    diffMin = np.amin(dataDiff)
    diffMean = np.mean(dataDiff)

    # Location of box
    nybox = int(nx * 0.2)
    nxbox = int(ny * 0.2)

    # Plot data
    # Figure 1 shows the result parameter data
    fig = plt.figure(figsize=(figW*3, figH))
    suptitle = fig.suptitle('%s' % avaName)
    ax1 = fig.add_subplot(131)
    cmap = cmapGB
    im1 = plt.imshow(data1, cmap=cmap, extent=[0, Lx, 0, Ly], origin='lower', aspect=nx/ny)
    fig.colorbar(im1, ax=ax1)
    ax1.set_aspect('auto')
    title = str('%s' % name1)
    ax1.set_title(title)
    ax1.set_xlabel('x [m]')
    ax1.set_ylabel('y [m]')
    ax2 = fig.add_subplot(132)
    im2 = plt.imshow(data2, cmap=cmap, extent=[0, Lx, 0, Ly], origin='lower', aspect=nx/ny)
    fig.colorbar(im2, ax=ax2)
    title2 = str('%s' % name2)
    ax2.set_title(title2)
    ax2.set_aspect('auto')
    ax2.set_xlabel('x [m]')
    title = str('%s' % name2)
    ax3 = fig.add_subplot(133)
    cmap = cmapdiv
    im3 = plt.imshow(dataDiff, cmap=cmap,
                     extent=[0, Lx, 0, Ly], origin='lower', aspect=nx/ny)
    fig.colorbar(im3, ax=ax3)
    ax3.text(nybox, nxbox, 'Mean: %.2f \n Max: %.2f \n Min: %.2f ' %
            (diffMean, diffMax, diffMin), bbox=dict(boxstyle="square", ec='white', fc='white'),
            horizontalalignment='left', verticalalignment='bottom')
    ax3.set_aspect('auto')
    ax3.set_xlabel('x [m]')
    ax3.set_title('Difference ref-sim')
    fig.tight_layout()
    fig.savefig(os.path.join(outDir, 'Diff_%s' % avaName))

    # Fgiure 2 cross and lonprofile
    fig, ax = plt.subplots(ncols=2, figsize=(figW*2, figH))
    suptitle = fig.suptitle('%s' % avaName)
    ax[0].plot(data1[:, ny_loc], 'k', label='data1')
    ax[0].plot(data2[:, ny_loc], 'b--', label='data2')
    ax[0].set_xlabel('Location across track [nrows]')
    ax[0].set_ylabel('Result parameter', fontsize=fs)
    ax[0].set_title('Cross profile at y =  %d' % ny_loc)
    ax[1].plot(data1[nx_loc, :], 'k', label='data1')
    ax[1].plot(data2[nx_loc, :], 'b--', label='data2')
    ax[1].set_xlabel('Location along track [ncols]')
    ax[1].set_ylabel('Result parameter', fontsize=fs)
    ax[1].set_title('Long profile at x =  %d' % nx_loc)

    ax[0].legend()
    ax[1].legend()
    fig.tight_layout()
    fig.savefig(os.path.join(outDir, 'Profiles_%s' % avaName))

    log.info('Figures saved to: %s' % outDir)
