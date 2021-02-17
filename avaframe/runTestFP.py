"""
    Run script for running python DFA kernel
"""
import os
import time
import numpy as np

# Local imports
import avaframe.in3Utils.initializeProject as initProj
import avaframe.in3Utils.fileHandlerUtils as fU
from avaframe.in1Data import getInput as gI
import avaframe.com1DFAPy.com1DFA as com1DFA
from avaframe.com1DFAPy import runCom1DFA
import avaframe.ana1Tests.FPtest as FPtest

# from avaframe.DFAkernel.setParam import *
from avaframe.in3Utils import cfgUtils
from avaframe.in3Utils import logUtils
import avaframe.out3Plot.makePalette as makePalette

# +++++++++SETUP CONFIGURATION++++++++++++++++++++++++
# log file name; leave empty to use default runLog.log
logName = 'runFlatPlaneTest'

# Load avalanche directory from general configuration file
cfgMain = cfgUtils.getGeneralConfig()
avalancheDir = 'data/avaFPtest'
# set module name, reqiured as long we are in dev phase
# - because need to create e.g. Output folder for com1DFAPy to distinguish from
# current com1DFA
modName = 'com1DFAPy'

# Clean input directory(ies) of old work and output files
initProj.cleanSingleAvaDir(avalancheDir, keep=logName)

# Start logging
log = logUtils.initiateLogger(avalancheDir, logName)
log.info('MAIN SCRIPT')
log.info('Current avalanche: %s', avalancheDir)

# Load configuration
FPCfg = os.path.join(avalancheDir, 'Inputs', 'FlatPlane_com1DFACfg.ini')
cfg = cfgUtils.getModuleConfig(com1DFA, FPCfg)
cfgGen = cfg['GENERAL']
cfgFP = cfg['FPSOL']

# for timing the sims
startTime = time.time()
# create output directory for test result plots
outDirTest = os.path.join(avalancheDir, 'Outputs', 'ana1Tests')
fU.makeADir(outDirTest)

# Define release thickness distribution
demFile, relFiles, entFiles, resFile, flagEntRes = gI.getInputData(
    avalancheDir, cfg['FLAGS'])
relDict = FPtest.getReleaseThickness(avalancheDir, cfg, demFile)
relTh = relDict['relTh']

# call com1DFAPy to perform simulation - provide configuration file and release thickness function
Particles, Fields, Tsave, dem = runCom1DFA.runCom1DFAPy(avaDir=avalancheDir, cfgFile=FPCfg, relTh=relTh, flagAnalysis=False)
relDict['dem'] = dem
# +++++++++POSTPROCESS++++++++++++++++++++++++
if cfgMain['FLAGS'].getboolean('showPlot'):
    # Analyse resutls
    outDirPlots = os.path.join(outDirTest, 'FPtest')
    fU.makeADir(outDirPlots)
    com1DFA.analysisPlots(Particles, Fields, cfg, relDict['demOri'], dem, outDirPlots)


# option for user interaction
if cfgFP.getboolean('flagInteraction'):
    showPlot = True
    value = input("give time step to plot (float in s):\n")
else:
    showPlot = cfgMain['FLAGS'].getboolean('showPlot')
    value = cfgFP.getfloat('dtSol')
try:
    value = float(value)
except ValueError:
    value = 'n'
while isinstance(value, float):
    ind_t = min(np.searchsorted(Tsave, value), len(Tsave)-1)

    # get particle parameters
    comSol = FPtest.postProcessFPcom1DFAPy(cfgGen, Particles, Fields, ind_t, relDict)
    comSol['outDirTest'] = outDirTest
    comSol['showPlot'] = showPlot
    comSol['Tsave'] = Tsave[ind_t]

    # make plot
    # TODO interaction
    FPtest.plotProfilesFPtest(cfg, ind_t, relDict, comSol)

    # option for user interaction
    if cfgFP.getboolean('flagInteraction'):
        value = input("give time step to plot (float in s):\n")
        try:
            value = float(value)
        except ValueError:
            value = 'n'
    else:
        value = 'n'
