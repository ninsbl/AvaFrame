"""
    Run com1DFA kernel and compare it tothe similarity solution
    This script computes the similarity solution for a gliding avalanche on
    a inclined plane according to similarity solution from :
    Hutter, K., Siegel, M., Savage, S.B. et al.
    Two-dimensional spreading of a granular avalanche down an inclined plane
    Part I. theory. Acta Mechanica 100, 37–68 (1993).
    https://doi.org/10.1007/BF01176861
    and compares it to the DFA kernel com1DFA
"""

import pathlib

# Local imports
import avaframe.in3Utils.initializeProject as initProj
import avaframe.in3Utils.fileHandlerUtils as fU
from avaframe.in3Utils import cfgUtils
from avaframe.in3Utils import logUtils
import avaframe.ana1Tests.simiSolTest as simiSolTest
import avaframe.com1DFA.com1DFA as com1DFA


# +++++++++SETUP CONFIGURATION++++++++++++++++++++++++
# log file name; leave empty to use default runLog.log
logName = 'runSimilarityTest'

# Load general configuration
cfgMain = cfgUtils.getGeneralConfig()
avalancheDir = 'data/avaSimilaritySol'

# Clean input directory(ies) of old work and output files
# initProj.cleanSingleAvaDir(avalancheDir, keep=logName)
initProj.cleanModuleFiles(avalancheDir, module=com1DFA)

# Start logging
log = logUtils.initiateLogger(avalancheDir, logName)
log.info('MAIN SCRIPT')
log.info('Current avalanche: %s', avalancheDir)

# Load configuration for similarity solution test
simiSolCfg = pathlib.Path(avalancheDir, 'Inputs', 'simiSol_com1DFACfg.ini')

# create output directory for test result plots
outDirTest = pathlib.Path(avalancheDir, 'Outputs', 'ana1Tests')
fU.makeADir(outDirTest)

simiSolTest.mainCompareSimSolCom1DFA(avalancheDir, cfgMain, simiSolCfg, outDirTest)
