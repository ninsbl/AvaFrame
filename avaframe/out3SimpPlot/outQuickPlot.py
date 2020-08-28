"""

This is a simple function for a quick plot of datasets and option for comparison
between two datasets of identical shape. Also plots cross and longprofiles.

set desired values in

This file is part of Avaframe.

"""

import matplotlib.pyplot as plt
from avaframe.in3Utils import fileHandlerUtils as fU
import numpy as np
import os
import seaborn as sns
import logging
import shutil
import glob

# Local imports
from avaframe.out3SimpPlot.plotSettings import *

# create local logger
# change log level in calling module to DEBUG to see log messages
log = logging.getLogger(__name__)


def prepareData(avaDir, inputDir):
    """ Read all files in input directory and generate a dictionary
        with info on:

            files:      full file path
            values:     actual data (e.g. raster of peak pressure)
            names:      file name
            simType:    entres or null (e.g. entres is simulation with entrainment and resistance)
            resType:    which result parameter (e.g. 'ppr' is peak pressure)
    """

    # Load input datasets from input directory
    datafiles = glob.glob(inputDir+os.sep + '*.asc')

    # Make dictionary of input data info
    data = {'files' : [], 'values' : [], 'names' : [], 'resType' : [], 'simType' : []}
    for m in range(len(datafiles)):
        data['files'].append(datafiles[m])
        data['values'].append( np.loadtxt(datafiles[m], skiprows=6))
        name = os.path.splitext(os.path.basename(datafiles[m]))[0]
        data['names'].append(name)
        data['simType'].append(name.split('_')[1])
        data['resType'].append(name.split('_')[3])

    return data


def quickPlot(avaDir, suffix, cfg, com1DFAOutput, simName):
    """ Plot two raster datasets of identical dimension:

        Inputs:

        avaDir          avalanche directory
        suffix          result parameter abbreviation (e.g. 'ppr')
        com1DFAOutput   folder where results to be plotted are located
        simName         entres or null for simulation type
        cfgR            configuration for plots

        Outputs:

        figure 1: plot raster data for dataset1, dataset2 and their difference
        figure 2: plot cross and longprofiles for both datasets (ny_loc and nx_loc define location of profiles)
        -plots are saved to Outputs/out3SimpPlot
    """

    # Create required directories
    workDir = os.path.join(avaDir, 'Work', 'out3SimplPlot')
    fU.makeADir(workDir, flagRemDir=True)
    outDir = os.path.join(avaDir, 'Outputs', 'out3SimplPlot')
    fU.makeADir(outDir, flagRemDir=False)

    # Setup input from com1DFA
    fU.getDFAData(avaDir, com1DFAOutput, workDir, suffix)

    # Get data from reference run
    fU.getRefData(avaDir, workDir, suffix)

    # prepare data
    data = prepareData(avaDir, workDir)

    # get list of indices of files that are of correct simulation type and result paramete
    indSuffix = []
    for m in range(len(data['files'])):
        if data['resType'][m] == suffix and data['simType'][m] == simName:
            indSuffix.append(m)

    # Load data
    data1 = data['values'][indSuffix[0]]
    data2 = data['values'][indSuffix[1]]
    ny = data1.shape[0]
    nx = data1.shape[1]
    log.info('dataset1: %s' % data['files'][indSuffix[0]])
    log.info('dataset2: %s' % data['files'][indSuffix[1]])

    # Location of Profiles
    ny_loc = int(nx *0.5)
    nx_loc = int(ny *0.5)

    # Plot data
    # Figure 1 shows the result parameter data
    fig = plt.figure(figsize=(figW*3, figH), dpi=figReso)
    ax1 = fig.add_subplot(131)
    ax2 = fig.add_subplot(132)
    ax3 = fig.add_subplot(133)
    cmap = cmapGB
    sns.heatmap(data1, cmap=cmap, ax=ax1, xticklabels=False, yticklabels=False)
    sns.heatmap(data2, cmap=cmap, ax=ax2, xticklabels=False, yticklabels=False)
    sns.heatmap(data1-data2, cmap=cmapdiv, ax=ax3, xticklabels=False, yticklabels=False)
    ax1.set_title('%s' % data['names'][indSuffix[0]])
    ax1.invert_yaxis()
    ax2.invert_yaxis()
    ax3.invert_yaxis()
    ax2.set_title('%s' % data['names'][indSuffix[1]])
    ax3.set_title('Difference ref-sim')
    fig.savefig(os.path.join(outDir, 'refDfa_%s.png' % suffix))

    # Fgiure 2 cross and lonprofile
    fig, ax = plt.subplots(ncols=2, figsize=(figW*2, figH), dpi=figReso)
    ax[0].plot(data1[:, ny_loc], 'k', linewidth=lw, label='Reference')
    ax[0].plot(data2[:, ny_loc], 'b--', label='Simulation')
    ax[0].set_xlabel('Location across track [nrows]')
    ax[0].set_ylabel('Result parameter %s' % suffix, fontsize=fs)
    ax[0].set_title('Cross profile at y =  %d' % ny_loc)
    plt.legend()
    ax[1].plot(data1[nx_loc, :], 'k', linewidth=lw, label='Reference')
    ax[1].plot(data2[nx_loc, :], 'b--', label='Simulation')
    ax[1].set_xlabel('Location along track [ncols]')
    ax[1].set_ylabel('Result parameter %s' % suffix, fontsize=fs )
    ax[1].set_title('Long profile at x =  %d' % nx_loc)

    ax[0].legend()
    ax[1].legend()
    fig.savefig(os.path.join(outDir, 'refDfaProfiles_%s.png' % suffix))

    log.info('Figures saved to: %s' % outDir)

    if cfg['FLAGS'].getboolean('showPlot'):
        plt.show()
