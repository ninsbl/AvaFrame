"""
    Python wrapper to execute the compiled com1Exe file and set desired simulation options
"""

# Load modules
import os
import subprocess
import shutil
import logging
import numpy as np

# Local imports
from avaframe.in3Utils import fileHandlerUtils as fU
from avaframe.in2Trans import ascUtils as aU
from avaframe.in3Utils import initialiseDirs as iD
from avaframe.in1Data import getInput as gI
from avaframe.in2Trans import shpConversion as sP

# create local logger
# change log level in calling module to DEBUG to see log messages
log = logging.getLogger(__name__)


def execCom1Exe(com1Exe, cintFile, avaDir, fullOut=False, simName=''):
    """ Execute compiled com1Exe file using cintFile to set configuration
        and run options

        Parameters
        ----------
        com1Exe : str
            path to com1Exe
        cintFile : str
            path to cint file
        avaDir : str
            path to avalanche directoy
        fullOut : bool
            flag if True print full output from com1Exe to terminal and log, default False
        simName : str
            optional - name of simulation, will be used to create a log
    """

    # define command line
    runCommand = com1Exe + ' -offscreen ' + cintFile

    # initialise log file to save stoudt
    if simName != '':
        f_log = open(os.path.join(avaDir, 'Outputs', 'com1DFA', 'start%s.log' % (simName)), 'w')

    # Call command
    proc = subprocess.Popen(runCommand, shell=True, stdout=subprocess.PIPE,
                            universal_newlines=True)

    # loop through output and save to logFile if file provided
    for line in proc.stdout:
        if simName != '':
            f_log.write(line)
        if fullOut:
            log.info((line.rstrip()))
        elif 'BatchCom1DFA' in line:
            if 'Computing' in line:
                log.info(line.rstrip())
            else:
                log.debug(line.rstrip())
        elif 'error' in line:
            log.info(line.rstrip())

    # make process wait for previous process to finish
    reVal = proc.wait()


def copyReplace(origFile, workFile, searchString, replString):
    """ Modifiy cintFiles to be used to set simulation configuration"""

    # Check if input files match, if not save origFile to workFile
    try:
        shutil.copy2(origFile, workFile)
    except shutil.SameFileError:
        pass

    # Read file
    fileData = None
    with open(workFile, 'r') as file:
        fileData = file.read()

    # Replace target string
    fileData = fileData.replace(searchString, str(replString))

    # Write new info to file
    with open(workFile, 'w') as file:
        file.write(fileData)


def com1DFAMain(cfg, avaDir):
    """ Run main model

    This will compute a dense flow avalanche

    Parameters
    ----------
    cfg : dict
        configuration read from ini file
    avaDir : str
        path to avalanche directory

    Returns
    -------
    reportDictList : list
        list of dictionaries that contain information on simulations that can be used for report generation
    """

    # Setup configuration
    cfgGen = cfg['GENERAL']
    com1Exe = cfgGen['com1Exe']
    modName = 'com1DFA'
    flagEnt = cfgGen.getboolean('flagEnt')
    flagRes = cfgGen.getboolean('flagRes')
    fullOut = cfgGen.getboolean('flagOut')
    cfgPar = cfg['PARAMETERVAR']
    resDir = os.path.join(avaDir, 'Work', 'com1DFA')
    # Get path of module
    modPath = os.path.dirname(__file__)
    # Standard values for parameters that can be varied
    defValues = cfg['DEFVALUES']

    # Log chosen settings
    log.debug('The chosen settings: entrainment - %s , resistance - %s ' % (flagEnt, flagRes))

    # Log current avalanche directory
    log.debug('Your current avalanche name: %s' % avaDir)

    # Create output and work directories
    workDir, outDir = iD.initialiseRunDirs(avaDir, modName)

    # Load input data
    dem, rels, ent, res, flagEntRes = gI.getInputData(avaDir, cfgGen)
    entrainmentArea = ''
    resistanceArea = ''
    if flagEntRes:
        entrainmentArea = os.path.splitext(os.path.basename(ent))[0]
        resistanceArea = os.path.splitext(os.path.basename(res))[0]

    # Parameter variation
    if cfgPar.getboolean('flagVarPar'):
        varPar = cfgPar['varPar']
    else:
        varPar = 'Mu'

    # Initialise full experiment log file
    with open(os.path.join(workDir, 'ExpLog.txt'), 'w') as logFile:
        logFile.write("NoOfSimulation,SimulationRunName,%s\n" % varPar)

    # Counter for release area loop
    countRel = 0

    # Setup simulation dictionaries for report genereation
    reportDictList = []

    # Loop through release areas
    for rel in rels:

        # Set release areas and simulation name
        relName = os.path.splitext(os.path.basename(rel))[0]
        simName = relName
        relDict = sP.SHP2Array(rel)
        for k in range(len(relDict['d0'])):
            if relDict['d0'][k] == 'None':
                relDict['d0'][k] = '1.0'
        log.info('Release area scenario: %s - perform simulations' % (relName))
        if flagEntRes:
            log.info('Entrainment area: %s and resistance area: %s' % (entrainmentArea, resistanceArea))

        # Initialise CreateProject cint file
        templateFile = os.path.join(modPath, 'CreateProject.cint')
        workFile = os.path.join(avaDir, 'Work', 'com1DFA', 'CreateProject.cint')
        projDir = os.path.join(avaDir, 'Work', 'com1DFA', simName)
        demName = os.path.splitext(os.path.basename(dem))[0]

        # Set Parameters in cint file
        copyReplace(templateFile, workFile, '##PROJECTDIR##', projDir)
        copyReplace(workFile, workFile, '##DHMFILE##', dem)
        copyReplace(workFile, workFile, '##DHMNAME##', demName)
        copyReplace(workFile, workFile, '##RELFILE##', rel)
        copyReplace(workFile, workFile, '##ENTFILE##', ent)
        copyReplace(workFile, workFile, '##RESFILE##', res)
        # Setup Project
        execCom1Exe(com1Exe, workFile, avaDir, fullOut)

        if flagEntRes:
            # Initialise CreateSimulations cint file and set parameters
            templateFile = os.path.join(modPath, 'CreateEntResSimulations.cint')
            workFile = os.path.join(avaDir, 'Work', 'com1DFA', 'CreateEntResSimulations.cint')
            cuSim = [simName + '_entres_dfa', simName + '_null_dfa']
        else:
            # Initialise CreateSimulations cint file and set parameters
            templateFile = os.path.join(modPath, 'CreateNullSimulation.cint')
            workFile = os.path.join(avaDir, 'Work', 'com1DFA', 'CreateNullSimulation.cint')
            cuSim = [simName + '_null_dfa']

        # Write required info to cint file
        copyReplace(templateFile, workFile, '##PROJECTDIR##', projDir)
        copyReplace(workFile, workFile, '##BASESIMNAME##', simName)
        execCom1Exe(com1Exe, workFile, avaDir, fullOut)

        # If parameter shall be varied
        if cfgPar.getboolean('flagVarPar'):

            # Also perform one standard simulation
            simST = simName + '_null_dfa'
            logName = simST + '_' + defValues[cfgPar['varPar']]
            log.info('Also perform one standard simulation: %s' % simST)
            templateFile = os.path.join(modPath, 'runStandardSimulation.cint')
            workFile = os.path.join(avaDir, 'Work', 'com1DFA', 'runStandardSimulation.cint')
            # Write required info to cint file
            copyReplace(templateFile, workFile, '##PROJECTDIR##', projDir)
            copyReplace(workFile, workFile, '##RESDIR##', resDir)
            copyReplace(workFile, workFile, '##NAME##', simST)
            copyReplace(workFile, workFile, '##COUNTREL##', countRel)
            copyReplace(workFile, workFile, '##VARPAR##', cfgPar['varPar'])
            copyReplace(workFile, workFile, '##VALUE##', defValues[cfgPar['varPar']])
            execCom1Exe(com1Exe, workFile, avaDir, fullOut, logName)

            # Create dictionary
            reportNull = {}
            reportNull = {'headerLine': {'type': 'title', 'title': 'com1DFA Simulation'},
            'simName': {'type': 'simName', 'name': logName},
                'Simulation Parameters': {
                    'type': 'list',
                    'Release Area Scenario': relName,
                    'Release Area': relDict['Name'],
                    'Entrainment Area': '',
                    'Resistance Area': '',
                    'Parameter variation on': '',
                    'Parameter value': '',
                    'Mu': defValues['Mu'],
                    'Release thickness [m]': relDict['d0']},
                'Release area': {'type': 'columns', 'Release area scenario': relName}}

            # Add to report dictionary list
            reportDictList.append(reportNull)

            # Count total number of simulations
            countRel = countRel + 1

            if cfgPar.getboolean('flagVarEnt') and (simName + '_entres_dfa') in cuSim:
                sim = simName + '_entres_dfa'
                log.info('Parameter variation used including entrainment and resistance, varying: %s' % cfgPar['varPar'])
            else:
                sim = simName + '_null_dfa'
                log.info('Parameter variation used not including entrainment and resistance, varying: %s' % cfgPar['varPar'])

            # Values of parameter variations in config file as string
            varParValues = cfg['PARAMETERVAR']['varParValues']
            if '_' in varParValues:
                itemsRaw = varParValues.split('_')
                items = []
            elif ':' in varParValues:
                itemsInput = varParValues.split(':')
                itemsRaw = np.linspace(float(itemsInput[0]), float(itemsInput[1]), int(itemsInput[2]))
            items = []
            for itemR in itemsRaw:
                items.append('%.5f' % float(itemR))
            for item in items:
                logName = sim + '_' + item
                log.info('Perform simulation with %s = %s: logName = %s' % (cfgPar['varPar'], item, logName))
                templateFile = os.path.join(modPath, '%s%s.cint' % (cfgPar['varRunCint'], cfgPar['varPar']))
                workFile = os.path.join(avaDir, 'Work', 'com1DFA',
                                        '%s%sBasic.cint' % (cfgPar['varRunCint'], cfgPar['varPar']))
                copyReplace(templateFile, workFile, '##PROJECTDIR##', projDir)
                copyReplace(workFile, workFile, '##RESDIR##', resDir)
                copyReplace(workFile, workFile, '##NAME##', sim)
                copyReplace(workFile, workFile, '##COUNTREL##', countRel)
                copyReplace(workFile, workFile, '##VALUE##', item)
                execCom1Exe(com1Exe, workFile, avaDir, fullOut, logName)

                # Create dictionary
                reportVar = {}
                reportVar = {'headerLine': {'type': 'title', 'title': 'com1DFA Simulation'},
                'simName': {'type': 'simName', 'name': logName},
                    'Simulation Parameters': {
                        'type': 'list',
                        'Release Area Scenario': relName,
                        'Release Area': relDict['Name'],
                        'Entrainment Area': entrainmentArea,
                        'Resistance Area': resistanceArea,
                        'Parameter variation on': cfgPar['varPar'],
                        'Parameter value': item},
                    'Release area': {'type': 'columns', 'Release area scenario': relName},
                    'Entrainment area': {'type': 'columns', 'Entrainment area scenario': entrainmentArea},
                    'Resistance area': {'type': 'columns', 'Resistance area scenario': resistanceArea}}

                if cfgPar['varPar'] == 'RelTh':
                    reportVar['Simulation Parameters'].update({'Mu': defValues['Mu']})
                    reportVar['Simulation Parameters'].update({'Release thickness [m]': item})
                elif cfgPar['varPar'] == 'Mu':
                    reportVar['Simulation Parameters'].update({'Release thickness [m]': relDict['d0']})
                    reportVar['Simulation Parameters'].update({'Mu': item})

                # Add to report dictionary list
                reportDictList.append(reportVar)

                # Count total number of simulations
                countRel = countRel + 1

        else:
            for sim in cuSim:
                if flagEntRes:
                    log.debug('One simulation is performed using entrainment and \
                               one standard simulation without')
                else:
                    log.debug('Standard simulation is performed without entrainment and resistance')
                templateFile = os.path.join(modPath, 'runStandardSimulation.cint')
                workFile = os.path.join(avaDir, 'Work', 'com1DFA', 'runStandardSimulation.cint')
                logName = sim + '_' + defValues['Mu']
                # Write required info to cint file
                copyReplace(templateFile, workFile, '##PROJECTDIR##', projDir)
                copyReplace(workFile, workFile, '##RESDIR##', resDir)
                copyReplace(workFile, workFile, '##NAME##', sim)
                copyReplace(workFile, workFile, '##COUNTREL##', countRel)
                copyReplace(workFile, workFile, '##VARPAR##', 'Mu')
                copyReplace(workFile, workFile, '##VALUE##', defValues['Mu'])
                execCom1Exe(com1Exe, workFile, avaDir, fullOut, logName)

                # Create dictionary
                reportST = {}
                reportST = {}
                reportST = {'headerLine': {'type': 'title', 'title': 'com1DFA Simulation'},
                'simName': {'type': 'simName', 'name': logName},
                    'Simulation Parameters': {
                        'type': 'list',
                        'Release Area Scenario': relName,
                        'Release Area': relDict['Name'],
                        'Entrainment Area': '',
                        'Resistance Area': '',
                        'Parameter variation on': '',
                        'Parameter value': '',
                        'Mu': defValues['Mu'],
                        'Release thickness [m]': relDict['d0']},
                    'Release Area': {'type': 'columns', 'Release area scenario': relName}}

                if 'entres' in sim:
                    reportST['Simulation Parameters'].update({'Entrainment Area': entrainmentArea})
                    reportST['Simulation Parameters'].update({'Resistance Area': resistanceArea})
                    reportST.update({'Entrainment area': {'type': 'columns', 'Entrainment area scenario': entrainmentArea}})
                    reportST.update({'Resistance area': {'type': 'columns', 'Resistance area scenario': resistanceArea}})

                # Add to report dictionary list
                reportDictList.append(reportST)

                # Count total number of simulations
                countRel = countRel + 1

    log.debug('Avalanche Simulations performed')

    # Setup input from com1DFA and exort to Outputs/com1DFA
    if cfgPar.getboolean('flagVarPar'):
        fU.exportcom1DFAOutput(avaDir, cfgPar)
    else:
        fU.exportcom1DFAOutput(avaDir)

    log.info('Exported results to Outputs/com1DFA')

    return reportDictList
