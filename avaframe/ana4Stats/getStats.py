"""

Function to determine statistics of datasets

"""

import os
import numpy as np
import logging
import pathlib
from matplotlib import pyplot as plt

from avaframe.in3Utils import fileHandlerUtils as fU
import avaframe.in2Trans.ascUtils as IOf
from avaframe.in3Utils import cfgUtils


# create local logger
# change log level in calling module to DEBUG to see log messages
log = logging.getLogger(__name__)


def readAimecRunout(workingDir, avaName, cfg):
    """ Read runout length from aimec results

        Parameters
        ----------
        workingDir: str
            path to avalanche aimec directoy
        avaName: str
            name of avalanche directoy
        cfg : dict
            configuration read from ini file of aimec

        Returns
        --------
        Lrun: numpy array 1D
            runout length from aimec analaysis

    """

    # load configuration
    pLim = cfg['pressureLimit']
    dWidth = cfg['domainWidth']

    # set input file
    inputFileName = 'Results_%s__com1DFA__plim_%s_w_%s.txt' % (avaName, pLim, dWidth)
    inputFile = pathlib.Path(workingDir, inputFileName)
    dataset = np.loadtxt(inputFile, skiprows=7)
    Lrun = dataset[:, 3]

    return Lrun


def extractMaxValues(inputDir, avaDir, varPar, restrictType='', nameScenario='', parametersDict=''):
    """ Extract max values of result parameters and save to dictionary

        - optionally restrict data of peak fields by defining which result parameter with restrictType,
          provide nameScenario and a parametersDict to filter simulations

        Parameters
        -----------
        inputDir: str
            path to directoy where peak files can be found
        avaDir: str
            path to avalanche directoy
        varPar: str
            parameter that has been varied when performing simulations (for example relTh)
        restrictType: str
            optional -result type of result parameters that should be used to mask result fields (eg. ppr, pfd, ..)
        nameScenario: str
            optional -parameter that shall be used for color coding of simulation results
            in plots (for example releaseScenario)
        parametersDict: dict
            optional -dictionary with parameter and parameter values to filter simulations

        Returns
        --------
        peakValues: dict
            dictionary that contains max values for all result parameters for
            each simulation
        """

    # filter simulation results using parametersDict
    simNameList = cfgUtils.filterSims(avaDir, parametersDict)
    # load dataFrame of all simulation configurations
    simDF = cfgUtils.createConfigurationInfo(avaDir, standardCfg='')

    # load peakFiles of all simulations and generate dataframe
    peakFilesDF = fU.makeSimDF(inputDir, avaDir=avaDir)
    nSims = len(peakFilesDF['simName'])
    # initialize peakValues dictionary
    peakValues = {}
    for sName in simDF['simName'].tolist():
        peakValues[sName] = {}

    # Loop through result field files and compute statistical measures
    for m in range(nSims):
        # filter simulations according to parametersDict
        if peakFilesDF['simName'][m] in simNameList:

            # Load data
            fileName = peakFilesDF['files'][m]
            simName = peakFilesDF['simName'][m]
            dataFull = IOf.readRaster(fileName)

            # if restrictType, set result field values to nan if restrictType result field equals 0
            if restrictType != '':
                peakFilesSimName = peakFilesDF[peakFilesDF['simName'] == simName]
                fileNamePFD = peakFilesSimName[peakFilesSimName['resType'] == restrictType]['files'].values[0]
                dataPFD = IOf.readRaster(fileNamePFD)
                data = np.where((dataPFD['rasterData'] == 0.0), np.nan, dataFull['rasterData'])
            else:
                data = dataFull['rasterData']

            # compute max, mean, min and standard deviation of result field
            max = np.nanmax(data)
            min = np.nanmin(data)
            mean = np.nanmean(data)
            std = np.nanstd(data)
            statVals = {'max': max, 'min': min, 'mean': mean, 'std': std}
            # add statistical measures
            peakValues[simName].update({peakFilesDF['resType'][m]: statVals})

            # fetch varPar value and nameScenario
            varParVal = simDF[simDF['simName'] == simName][varPar]
            peakValues[simName].update({'varPar': float(varParVal)})
            if nameScenario != '':
                nameScenarioVal = simDF[simDF['simName'] == simName][nameScenario]
                peakValues[simName].update({'scenario': nameScenarioVal[0]})
                log.info('Simulation parameter %s= %s for resType: %s and name %s' %
                        (varPar, varParVal[0], peakFilesDF['resType'][m], nameScenarioVal[0]))
            else:
                log.info('Simulation parameter %s= %s for resType: %s' %
                        (varPar, varParVal[0], peakFilesDF['resType'][m]))
        else:
            peakValues.pop(peakFilesDF['simName'][m], None)

    return peakValues
