"""

This is a simple function for computing a mask of all peak files of one parameter that exceed a particular threshold

This file is part of Avaframe.

"""

import os
import numpy as np
import logging
from matplotlib import pyplot as plt

from avaframe.out3Plot.plotUtils import *
from avaframe.in3Utils import fileHandlerUtils as fU
import avaframe.out3Plot.makePalette as makePalette
import avaframe.in2Trans.ascUtils as IOf

# create local logger
# change log level in calling module to DEBUG to see log messages
log = logging.getLogger(__name__)


def probAnalysis(avaDir, cfg, cfgMain, inputDir='', outDir=''):
    """ perform analysis """

    # Set input and output directory
    if inputDir == '':
        inputDir = os.path.join(avaDir, 'Outputs', 'com1DFA', 'peakFiles')
        outDir = os.path.join(avaDir, 'Outputs', 'ana4Prob')
        fU.makeADir(outDir)

    # Load all infos on simulations
    peakFiles = fU.makeSimDict(inputDir, cfgMain['PARAMETERVAR']['varPar'], avaDir)

    # get header info from peak files
    header = IOf.readASCheader(peakFiles['files'][0])
    cellSize = header.cellsize
    nRows = header.nrows
    nCols = header.ncols
    xllcenter = header.xllcenter
    yllcenter = header.yllcenter
    noDataValue = header.noDataValue

    # Initialise array for computations
    probSum = np.zeros((nRows, nCols))
    count = 0

    # Loop through peakFiles and compute probability
    for m in range(len(peakFiles['names'])):

        # Load peak field for desired peak field parameter
        # be aware of the standard simulation - so if default value should not be part of the analysis
        if peakFiles['resType'][m] == cfg['GENERAL']['peakVar'] and peakFiles[cfgMain['PARAMETERVAR']['varPar']][m] != cfgMain['DEFVALUES'][cfgMain['PARAMETERVAR']['varPar']]:
            log.info('Simulation parameter %s= %s ' % (cfgMain['PARAMETERVAR']['varPar'], peakFiles[cfgMain['PARAMETERVAR']['varPar']][m]))

            # Load data
            fileName = peakFiles['files'][m]
            data = np.loadtxt(fileName, skiprows=6)
            dataLim = np.zeros((nRows, nCols))

            # Check if peak values exceed desired threshold
            dataLim[data>float(cfg['GENERAL']['peakLim'])] = 1.0
            probSum = probSum + dataLim
            count = count + 1

    # Create probability map ranging from 0-1
    probMap = probSum / count
    unit = cfgMain['REPORT']['unit%s' % cfg['GENERAL']['peakVar']]
    log.info('probability analysis performed for peak parameter: %s and a peak value threshold of: %s %s' % (cfg['GENERAL']['peakVar'], cfg['GENERAL']['peakLim'], unit))
    log.info('%s peak fields added to analysis' % count)


    # Save to .asc file
    probMap = np.matrix(probMap)
    avaName = os.path.basename(avaDir)
    with open(os.path.join(outDir, '%s_probMap.asc' % avaName), 'w') as f:
        f.write('nCols  %d\n' % (nCols))
        f.write('nRows  %d\n' % (nRows))
        f.write('xllcenter  %.02f\n' % (xllcenter))
        f.write('yllcenter %.02f\n' % (yllcenter))
        f.write('cellsize  %d\n' % (cellSize))
        f.write('nodata_value %.02f\n' % (noDataValue))
        for line in probMap:
            np.savetxt(f, line, fmt='%f')
