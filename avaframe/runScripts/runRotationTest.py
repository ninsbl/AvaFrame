"""
Run the rotation test
Analyze the effect of the grid direction on DFA simulation results
"""
import pathlib

# Local imports
# import config and init tools
from avaframe.in3Utils import initializeProject as iP
from avaframe.in3Utils import cfgUtils
from avaframe.in3Utils import logUtils

# import analysis modules
from avaframe.ana3AIMEC import ana3AIMEC
from avaframe.ana1Tests import rotationTest

# +++++++++REQUIRED+++++++++++++
# log file name; leave empty to use default runLog.log
logName = 'runRotationTest'
# do you want to run the DFA module (all results in the Outputs/com1DFA forlder will be deleted)
runDFAModule = False
# for aimec analysis
anaMod = 'com1DFARotated'
referenceSimName = 'rel0'
flagMass = 'False'
# ++++++++++++++++++++++++++++++

# Load avalanche directory from general configuration file
cfgMain = cfgUtils.getGeneralConfig()
avalancheDir = cfgMain['MAIN']['avalancheDir']
avalancheDir = pathlib.Path(avalancheDir)

# Start logging
log = logUtils.initiateLogger(avalancheDir, logName)
log.info('MAIN SCRIPT')
log.info('Current avalanche: %s', avalancheDir)

# ----------------
# Clean input directory(ies) of old work and output files
iP.cleanSingleAvaDir(avalancheDir, keep=logName, deleteOutput=False)

# prepare the configuration
cfgAimec = cfgUtils.getModuleConfig(ana3AIMEC)
cfgSetup = cfgAimec['AIMECSETUP']
cfgSetup['referenceSimName'] = referenceSimName
cfgSetup['anaMod'] = anaMod
cfgAimec['FLAGS']['flagMass'] = flagMass

rotationTest.mainRotationTest(cfgMain, cfgAimec, runDFAModule)
