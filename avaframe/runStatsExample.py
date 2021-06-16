"""
    Run script for computing statistics of results including the runout derived from aimec
"""

# Load modules
import os
import time
import glob
import configparser
import shutil
import numpy as np

# Local imports
from avaframe.out3Plot import statsPlots as sPlot
import avaframe.com1DFA.com1DFA as com1DFA
import avaframe.ana4Stats.probAna as probAna
from avaframe.ana4Stats import getStats
from avaframe.runCom1DFA import runCom1DFA
from avaframe.ana3AIMEC import ana3AIMEC, dfa2Aimec
from avaframe.in3Utils import initializeProject as initProj
from avaframe.in3Utils import fileHandlerUtils as fU
from avaframe.log2Report import generateReport as gR
from avaframe.out1Peak import outPlotAllPeak as oP
from avaframe.out3Plot import plotUtils
from avaframe.in3Utils import cfgUtils
from avaframe.in3Utils import logUtils


# log file name; leave empty to use default runLog.log
logName = 'runGetStats'
modName = 'com1DFA'

# Load general configuration filee
cfgMain = cfgUtils.getGeneralConfig()
flagShow = cfgMain['FLAGS'].getboolean('showPlot')

avaDir = 'data/avaHockeyChannel'
cfgFull = cfgUtils.getModuleConfig(getStats)
cfg = cfgFull['GENERAL']
# Clean input directory(ies) of old work and output files
initProj.cleanSingleAvaDir(avaDir, keep=logName)

# set output directory, first ava in list
outDir = os.path.join(avaDir, 'Outputs', 'ana4Stats')
cfg['outDir'] = outDir
# Specify where you want the results to be stored
fU.makeADir(outDir)

# Start logging
log = logUtils.initiateLogger(outDir, logName)

# --- run Com1DFA -----
avaName = os.path.basename(avaDir)
avaNameTest = avaName + 'StatsTest'
statsSimCfg = os.path.join('..', 'benchmarks', avaNameTest, '%sStats_com1DFACfg.ini' % (avaName))

# Run Standalone DFA
particlesList, fieldsList, Tsave, dem, plotDict, reportDictList = runCom1DFA(avaDir=avaDir, cfgFile=statsSimCfg, relThField='', variationDict='')

if cfg.getboolean('aimec') == True:
    # run aimec
    statsAimecCfg = os.path.join('..', 'benchmarks', avaNameTest, '%sStats_ana3AIMECCfg.ini' % (avaName))
    cfgAIMEC = cfgUtils.getModuleConfig(ana3AIMEC, statsAimecCfg)
    cfgAimecSetup = cfgAIMEC['AIMECSETUP']

    # Setup input from com1DFA
    dfa2Aimec.mainDfa2Aimec(avaDir, cfgAimecSetup, modName)
    # Extract input file locations
    cfgPath = ana3AIMEC.readAIMECinputs(avaDir, dirName='com1DFA')
    # Run AIMEC postprocessing
    ana3AIMEC.mainAIMEC(cfgPath, cfgAIMEC)


# ----- determine max values of peak fields
# set directory of peak files
inputDir = os.path.join(avaDir, 'Outputs', modName, 'peakFiles')

# get max values of peak files
cfgDFA = cfgUtils.getModuleConfig(com1DFA, fileOverride=statsSimCfg)

# Load input parameters from configuration file
cfgStats = cfgUtils.getModuleConfig(getStats)

# provide optional filter criteria for simulations
parametersDict = fU.getFilterDict(cfgStats, 'FILTER')

# get statisical measure of simulations
peakValues = getStats.extractMaxValues(inputDir, cfgDFA, avaDir, cfgStats['GENERAL']['varPar'], nameScenario=cfgStats['GENERAL']['nameScenario'], parametersDict=parametersDict)

# log to screen
for key in peakValues:
    print('peakValues:', key, peakValues[key])

#++++++++++++++ Plot max values +++++++++++++++++
sPlot.plotValuesScatter(peakValues, 'pfd', 'pfv', 'relTh', cfg, avaDir, flagShow)
sPlot.plotValuesScatterHist(peakValues, 'pfd', 'pfv', 'relTh', cfg, avaDir, flagShow, flagHue=True)

log.info('Plots have been saved to: %s' % outDir)
