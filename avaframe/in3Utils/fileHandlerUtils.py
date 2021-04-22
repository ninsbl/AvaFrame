"""
    Directory and file handling helper functions
"""

# Load modules
import os
import glob
import logging
import numpy as np
import shutil

# Local imports
import avaframe.in2Trans.ascUtils as IOf


# create local logger
# change log level in calling module to DEBUG to see log messages
log = logging.getLogger(__name__)


def makeADir(dirName):
    """ Create a directory and print warning if it already existed

        Parameters
        ----------
        dirName : str
            path of directory that should be made
        """

    # If directory already exists - Delete directory first is default
    if os.path.isdir(dirName):
        log.debug('Be careful directory %s already existed - data saved on top of it' % (dirName))
    else:
        os.makedirs(dirName)
    log.debug('Directory: %s created' % dirName)


def readLogFile(logName, cfg=''):
    """ Read experiment log file and make dictionary that contains general info on all simulations

        Parameters
        ----------
        logName : str
            path to log file
        cfg : dict
            optional - configuration read from com1DFA simulation

        Returns
        -------
        logDict : dict
            dictionary with number of simulation (noSim), name of simulation (simName),
            parameter variation, full name
    """

    # Read log file
    logFile = open(logName, 'r')
    log.debug('Take com1DFA full experiment log')

    # Parameter variation
    if cfg != '':
        varPar = cfg['varPar']
    else:
        varPar = 'Mu'

    # Save info to dictionary, add all result parameters that are saved in com1DFA Outputs
    logDict = {'noSim' : [], 'simName' : [], varPar: [], 'fullName' : []}

    lines = logFile.readlines()[1:]
    countSims = 1
    for line in lines:
        vals = line.strip().split()
        logDict['noSim'].append(countSims)
        logDict['simName'].append(vals[1])
        logDict[varPar].append(float(vals[2]))
        logDict['fullName'].append(vals[1] + '_' + '%.5f' % float(vals[2]))
        countSims = countSims + 1

    return logDict


def extractParameterInfo(avaDir, simName, reportD):
    """ Extract info about simulation parameters from the log file

        Parameters
        ----------
        avaDir : str
            path to avalanche
        simName : str
            name of the simulation

        Returns
        -------
        parameterDict : dict
            dictionary listing name of parameter and value; release mass, final time step and current mast
        """

    # Get info from ExpLog
    logName = os.path.join(avaDir, 'Outputs', 'com1DFA', 'ExpLog.txt')
    logDictExp = readLogFile(logName)
    names = logDictExp['fullName']
    simNames = sorted(set(names), key=lambda s: s.split("_")[3])

    # Initialise parameter dictionary
    parameterDict = {}

    # Initialise fields
    time = []
    mass = []
    entrMass = []
    stopCrit = ''
    flagNoStop = True
    # Read log file
    fileName = os.path.join(os.getcwd(), avaDir, 'Outputs', 'com1DFA', 'start%s.log' % (simName))
    with open(fileName, 'r') as file:
        for line in file:
            if "computing time step" in line:
                ltime = line.split()[3]
                timeNum = ltime.split('...')[0]
                time.append(float(timeNum))
            elif "entrained DFA mass" in line:
                entrMass.append(float(line.split()[3]))
            elif "total DFA mass" in line:
                mass.append(float(line.split()[3]))
            elif "Kinetische Energie" in line:
                stopCrit = 'kinetic energy %.2f of peak KE' % (float(line.split()[3]))
            elif "terminated" in line:
                stopTime = float(line.split()[5])


    # Set values in dictionary
    parameterDict['release mass [kg]'] = np.asarray(mass)[0]
    parameterDict['final time step [s]'] = np.asarray(time)[-1]
    parameterDict['current mass [kg]'] = np.asarray(mass)[-1]
    if stopCrit != '':
        parameterDict['stop criterion'] = stopCrit
    else:
        parameterDict['stop criterion'] = 'end time reached: %.2f s' % np.asarray(time)[-1]
    parameterDict['Avalanche run time [s]'] = '%.2f' % stopTime
    parameterDict['CPU time [s]'] = stopTime

    reportD['Simulation Parameters'].update({'Stop criterion': parameterDict['stop criterion']})
    reportD['Simulation Parameters'].update({'Avalanche run time [s]': parameterDict['final time step [s]']})

    return parameterDict, reportD


def checkCommonSims(logName, localLogName):
    """ Check which files are common between local and full ExpLog """

    if os.path.isfile(localLogName) == False:
        localLogName = logName

    # Read log files and extract info
    logDict = readLogFile(logName)
    logDictLocal = readLogFile

    # Identify common simulations
    setSim = set(logDictLocal['simName'])
    indSims = [i for i, item in enumerate(logDict['simName']) if item in setSim]

    log.info('Common simulations are: %d' % indSims)

    return indSims


def splitIniValueToArraySteps(cfgValues):
    """ read values in ini file and return numpy array of values, values can either be separated by |
        or provided in start:end:numberOfSteps format

        Parameters
        ----------
        cfgValues : str
            values of parameter to be read from ini file

        Returns
        --------
        items : 1D numpy array
            values as 1D numpy array
    """

    if ':' in cfgValues:
        itemsInput = cfgValues.split(':')
        items = np.linspace(float(itemsInput[0]), float(itemsInput[1]), int(itemsInput[2]))
    else:
        itemsL = cfgValues.split('|')
        items = np.array(itemsL, dtype=float)

    return items


def splitTimeValueToArrayInterval(cfgGen):
    """ read values in ini file and return numpy array of values, values can either be separated by |
        or provided in start:interval format

        Parameters
        ----------
        cfgGen: dict
            configuration settings

        Returns
        --------
        items : 1D numpy array
            values as 1D numpy array
    """
    cfgValues = cfgGen['tSteps']
    endTime = cfgGen.getfloat('tEnd')
    if ':' in cfgValues:
        itemsInput = cfgValues.split(':')
        if float(endTime - float(itemsInput[0])) < float(itemsInput[1]):
            items = np.array([float(itemsInput[0]), endTime])
        else:
            items = np.arange(float(itemsInput[0]), endTime, float(itemsInput[1]))
    elif cfgValues == '':
        items = np.array([endTime])
    else:
        itemsL = cfgValues.split('|')
        items = np.array(itemsL, dtype=float)
        items = sorted(items)
    if items[0] == 0:
        items = np.delete(items, 0)

    return items


def getDFAData(avaDir, workDir, suffix, comModule='com1DFA', nameDir=''):
    """ Export the required data from com1DFA output to Aimec Work directory and rename,
        if nameDir='', data from com1DFA output copied to workDir without renaming

        Parameters
        ----------
        avaDir : str
            path to avalanche directory
        workDir : str
            path to directory that data should be copied to
        suffix : str
            result parameter abbreviation (e.g. 'ppr')
        comModule : str
            optional - name of computational module (default is com1DFA)
        nameDir : str
            optional - name of subdirectory of workDir where data shall be copied to and
            in this case data files get renamed to 0000xx.txt xx is the number of the file
      """

    # Lead all infos on simulations
    inputDir = os.path.join(avaDir, 'Outputs', comModule, 'peakFiles')
    data = makeSimDict(inputDir)
    countSuf = 0
    for m in range(len(data['files'])):
        if data['resType'][m] == suffix:
            if nameDir == '':
                shutil.copy(data['files'][m], workDir)
            else:
                shutil.copy(data['files'][m], '%s/%s/%06d.txt' % (workDir, nameDir, countSuf+1))
                log.info('%s   : %s/%s/%06d.txt' % (data['files'][m], workDir, nameDir, countSuf+1))
            countSuf = countSuf + 1

def getDFADataPaths(avaDir, pathDict, suffix, comModule='', inputDir=''):
    """ Determine the paths of the required data from comModule output for Aimec

        Parameters
        ----------
        avaDir : str
            path to avalanche directory
        pathDict: dict
            dictionary with paths to simulation results
        suffix : str
            result parameter abbreviation (e.g. 'ppr')
        comModule : str
            optional - name of computational module (default is com1DFA)
      """

    # Lead all infos on simulations
    if inputDir == '':
        inputDir = os.path.join(avaDir, 'Outputs', comModule, 'peakFiles')
        if os.path.isdir(inputDir) == False:
            log.error('Input directory does not exist - check anaMod')

    data = makeSimDict(inputDir)
    for m in range(len(data['files'])):
        if data['resType'][m] == suffix:
            pathDict[suffix].append(data['files'][m])
            log.info('Added to pathDict: %s' % (data['files'][m]))

    return pathDict


def getRefData(testDir, outputDir, suffix, nameDir='', testDirFP=''):
    """ Grab reference data and save to outputDir

        Parameters
        ----------
        avaDir : str
            path to avalanche directory
        suffix : str
            result parameter abbreviation (e.g. 'ppr')
        outputDir: str
            path to directoy that files should be copied to
    """

    # Input directory and load input datasets
    if testDirFP != '':
        refDir = testDirFP
    else:
        refDir = os.path.join('..', 'benchmarks', testDir)

    print('refDir', refDir)

    # Create simulations dictionary
    data = makeSimDict(refDir)

    # copy these files to desired working directory for outQuickPlot
    for m in range(len(data['files'])):
        if data['resType'][m] == suffix:
            if nameDir != '':
                shutil.copy(data['files'][m], '%s/%s/000000.txt' % (outputDir, nameDir))
            else:
                shutil.copy2(data['files'][m], outputDir)

    # Give status information
    if os.path.isdir(refDir) == False:
        log.error('%s does not exist - no files for reference found' % refDir)
    elif data['files'] == []:
        log.error('No files found in %s' % refDir)
    else:
        log.debug('Reference files copied from directory: %s' % refDir)


def exportcom1DFAOutput(avaDir, cfg='', addTSteps=False):
    """ Export the simulation results from com1DFA output to desired location

        Parameters
        ----------
        avaDir: str
            path to avalanche directory
        cfg : dict
            configuration read from ini file that has been used for the com1DFA simulation
        addTSteps : bool
            if True: first and last time step of flow depth are exported

    """

    # Initialise directories
    inputDir = os.path.join(avaDir, 'Work', 'com1DFA')
    outDir = os.path.join(avaDir, 'Outputs', 'com1DFA')
    outDirPF = os.path.join(outDir, 'peakFiles')
    outDirRep = os.path.join(outDir, 'reports')
    makeADir(outDir)
    makeADir(outDirPF)
    makeADir(outDirRep)

    # Read log file information
    logName = os.path.join(inputDir, 'ExpLog.txt')
    if cfg != '':
        logDict = readLogFile(logName, cfg)
        varPar = cfg['varPar']
    else:
        logDict = readLogFile(logName)
        varPar = 'Mu'

    # Get number of values
    sNo = len(logDict['noSim'])

    # Path to com1DFA results
    resPath = os.path.join(inputDir, 'FullOutput_%s_' % varPar)

    if addTSteps == True:
        timeStepDir = os.path.join(outDirPF, 'timeSteps')
        makeADir(timeStepDir)

    # Export peak files and reports
    for k in range(sNo):
        pathFrom = os.path.join('%s%.05f' % (resPath, logDict[varPar][k]),
                                logDict['simName'][k], 'raster',
                                '%s_pfd.asc' % logDict['simName'][k])
        pathTo = os.path.join(outDirPF, '%s_%.05f_pfd.asc' % (logDict['simName'][k], logDict[varPar][k]))
        shutil.copy(pathFrom, pathTo)
        if addTSteps == True:
            pathFrom = os.path.join('%s%.05f' % (resPath, logDict[varPar][k]),
                                    logDict['simName'][k], 'raster',
                                    '%s_fd.asc' % logDict['simName'][k])
            pathTo = os.path.join(outDirPF, 'timeSteps', '%s_%.05f_tLast_fd.asc' % (logDict['simName'][k], logDict[varPar][k]))
            shutil.copy(pathFrom, pathTo)
        pathFrom = os.path.join('%s%.05f' % (resPath, logDict[varPar][k]),
                                logDict['simName'][k], 'raster',
                                '%s_ppr.asc' % logDict['simName'][k])
        pathTo = os.path.join(outDirPF, '%s_%.05f_ppr.asc' % (logDict['simName'][k], logDict[varPar][k]))
        shutil.copy(pathFrom, pathTo)
        pathFrom = os.path.join('%s%.05f' % (resPath, logDict[varPar][k]),
                                logDict['simName'][k], 'raster',
                                '%s_pv.asc' % logDict['simName'][k])
        pathTo = os.path.join(outDirPF, '%s_%.05f_pfv.asc' % (logDict['simName'][k], logDict[varPar][k]))
        shutil.copy(pathFrom, pathTo)
        pathFrom = os.path.join('%s%.05f' % (resPath, logDict[varPar][k]),
                                '%s.html' % logDict['simName'][k])
        pathTo = os.path.join(outDirRep, '%s_%.05f.html' % (logDict['simName'][k], logDict[varPar][k]))
        shutil.copy(pathFrom, pathTo)

    if addTSteps == True:

        # Export peak files and reports
        for k in range(sNo):
            pathFrom = os.path.join('%s%.05f' % (resPath, logDict[varPar][k]),
                                    '%s_tFirst_fd.txt' % logDict['simName'][k])
            pathTo = os.path.join(outDirPF, 'timeSteps', '%s_%.05f_tFirst_fd.asc'
                                               % (logDict['simName'][k], logDict[varPar][k]))
            shutil.copy(pathFrom, pathTo)

    # Export ExpLog to Outputs/com1DFA
    shutil.copy2(os.path.join('%s' % inputDir, 'ExpLog.txt'), outDir)


def makeSimDict(inputDir, varPar='', avaDir=''):
    """ Create a dictionary that contains all info on simulations that can then be used to filter simulations for example

        Parameters
        ----------
        inputDir : str
            path to directory of simulation results
        varPar : str
            optional - parameter that has been used in parameter variation - reqiured if parameter variation has been used
        avaDir : str
            optional - path to avalanche directory

        Returns
        -------
        data : dict
            dictionary with full file path, file name, release area scenario, simulation type (null/entres),
            model type (dfa, ref, etc.), parameter variation, result type (ppr, pfd, etc.), simulation name,
            cell size and optional name of avalanche
    """

    # Load input datasets from input directory
    datafiles = glob.glob(inputDir+os.sep + '*.asc')

    # Sort datafiles by name
    datafiles = sorted(datafiles)

    # Check if parameter variation other than Mu
    if varPar == '':
        varPar = 'Mu'

    # Set name of avalanche if avaDir is given
    # Make dictionary of input data info
    data = {'files': [], 'names': [], 'resType': [], 'simType': [], 'simName' : [],
            'modelType' : [], 'releaseArea': [], 'cellSize': [], varPar: [], 'timeStep': []}

    # Set name of avalanche if avaDir is given
    if avaDir != '':
        avaName = os.path.basename(avaDir)
        data.update({'avaName' : []})

    for m in range(len(datafiles)):
        data['files'].append(datafiles[m])
        name = os.path.splitext(os.path.basename(datafiles[m]))[0]
        data['names'].append(name)
        if '_AF_' in name:
            nameParts = name.split('_AF_')
            fNamePart = nameParts[0] + '_AF'
            infoParts = nameParts[1].split('_')

        else:
            nameParts = name.split('_')
            fNamePart = nameParts[0]
            infoParts = nameParts[1:]

        data['releaseArea'].append(fNamePart)
        data['simType'].append(infoParts[0])
        data['modelType'].append(infoParts[1])
        data[varPar].append(infoParts[2])
        data['resType'].append(infoParts[3])
        data['simName'].append(fNamePart + '_' + ('_'.join(infoParts[0:3])))

        header = IOf.readASCheader(datafiles[m])
        data['cellSize'].append(header.cellsize)
        if len(infoParts) == 5:
            data['timeStep'].append(infoParts[4])

        # Set name of avalanche if avaDir is given
        if avaDir != '':
            data['avaName'].append(avaName)

    return data
