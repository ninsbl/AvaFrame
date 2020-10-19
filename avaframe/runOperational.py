"""
    Run script for running the operational workflow
    This file is part of Avaframe.
"""

# Load modules
import os
import time
import logging

# Local imports
from avaframe.com1DFA import com1DFA
from avaframe.log2Report import generateReport as gR
from avaframe.out3SimpPlot import outPlotAllPeak as oP
from avaframe.in3Utils import cfgUtils
from avaframe.in3Utils import logUtils
from avaframe.in3Utils import initializeProject as initProj

# Time the whole shebang
startTime = time.time()

# log file name; leave empty to use default runLog.log
logName = 'runOperational'

# Load avalanche directory from general configuration file
# v0.1 -> one avalanche is fine,
# v0.2 -> if given dir contains more than one avalancheDir -> run loop
cfgMain = cfgUtils.getGeneralConfig()
avalancheDir = cfgMain['MAIN']['avalancheDir']

# Start logging
log = logUtils.initiateLogger(avalancheDir, logName)
log.info('MAIN SCRIPT')
log.info('Current avalanche: %s', avalancheDir)

log.setLevel(logging.DEBUG)

# ----------------
# Load input parameters from configuration files

# ----------------
# Clean input directory(ies) of old work and output files
initProj.cleanSingleAvaDir(avalancheDir)

# ----------------
# Run dense flow
# cfg = cfgUtils.getModuleConfig(com1DFA)
# reportDictList = com1DFA.runCom1DFA(cfg, avalancheDir)

# ----------------
# Run Alpha Beta
# reportDictList = com2AB.runAlphaBeta(cfg, avalancheDir)

# ----------------
# Collect results/plots/report  to a single directory
# make simple plots (com1DFA, com2AB)
# peak file plot

# Generata plots for all peakFiles
# plotDict = oP.plotAllPeakFields(avalancheDir, cfg, cfgMain['FLAGS'])

# Set directory for report
# reportDir = os.path.join(avalancheDir, 'Outputs', 'com1DFA', 'reports')
# write report
# gR.writeReport(reportDir, reportDictList, cfgMain['FLAGS'], plotDict)

# Print time needed
endTime = time.time()
log.info('Took %s seconds to calculate.' % (endTime - startTime))























