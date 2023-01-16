"""
    Fetch input data for avalanche simulations
"""

# Load modules
import os
import glob
import pathlib
import logging

# Local imports
from avaframe.in3Utils import cfgUtils
import avaframe.in2Trans.ascUtils as IOf
import avaframe.in2Trans.shpConversion as shpConv
import avaframe.com1DFA.deriveParameterSet as dP


# create local logger
# change log level in calling module to DEBUG to see log messages
log = logging.getLogger(__name__)


def readDEM(avaDir):
    """ read the ascii DEM file from a provided avalanche directory

    Parameters
    ----------
    avaDir : str
        path to avalanche directory

    Returns
    -------
    dem : dict
        dict with header and raster data
    """

    # get dem file name
    demSource = getDEMPath(avaDir)

    log.debug('Read DEM: %s' % demSource)

    dem = IOf.readRaster(demSource)

    return(dem)


def getDEMPath(avaDir):
    """ get the DEM file path from a provided avalanche directory

    Parameters
    ----------
    avaDir : str
        path to avalanche directory

    Returns
    -------
    demFile : str (first element of list)
        full path to DEM .asc file
    """

    # if more than one .asc file found throw error
    inputDir = pathlib.Path(avaDir, 'Inputs')
    demFile = list(inputDir.glob('*.asc'))
    if len(demFile) > 1:
        message = 'There should be exactly one topography .asc file in %s/Inputs/' % (avaDir)
        log.error(message)
        raise AssertionError(message)

    # if is no .asc file found - throw error
    filesFound = list(inputDir.glob('*.*'))
    if len(demFile) == 0 and len(filesFound):
        for fileF in filesFound:
            message = 'DEM file format not correct in %s/Inputs/ - only .asc is allowed but %s is provided' % (avaDir, fileF.name)
            log.error(message)
            raise AssertionError(message)
    elif len(demFile) == 0:
        message = 'No topography .asc file in %s/Inputs/' % (avaDir)
        log.error(message)
        raise FileNotFoundError(message)

    return demFile[0]


def getInputData(avaDir, cfg):
    """ Fetch input datasets required for simulation, duplicated function because
        simulation type set differently in com1DFAOrig compared to com1DFA:
        TODO: remove duplicate once it is not required anymore

    Parameters
    ----------
    avaDir : str
        path to avalanche directory
    cfg : dict
        configuration read from com1DFA simulation ini file

    Returns
    -------
    demFile[0] : str (first element of list)
        list of full path to DEM .asc file
    relFiles : list
        list of full path to release area scenario .shp files
    entFile : str
        full path to entrainment area .shp file
    resFile : str
        full path to resistance area .shp file
    wallFile: str
        full path to wall line .shp file
    entResInfo : flag dict
        flag if Yes entrainment and/or resistance areas found and used for simulation
    """

    # Set directories for inputs, outputs and current work
    inputDir = os.path.join(avaDir, 'Inputs')

    # Set flag if there is an entrainment or resistance area
    entResInfo= {'flagEnt': 'No', 'flagRes': 'No'}

    # Initialise release areas, default is to look for shapefiles
    if cfg['releaseScenario'] != '':
        releaseDir = 'REL'
        relFiles = []
        releaseFiles = cfg['releaseScenario'].split('|')
        for rel in releaseFiles:
            if '.shp' in rel:
                relf = os.path.join(inputDir, releaseDir, rel)
            else:
                relf = os.path.join(inputDir, releaseDir, '%s.shp' % (rel))
            if not os.path.isfile(relf):
                message = 'No release scenario called: %s' % (relf)
                log.error(message)
                raise FileNotFoundError(message)
            relFiles.append(relf)
        log.debug('Release area file is specified to be: %s' % relFiles)
    else:
        releaseDir = 'REL'
        relFiles = sorted(glob.glob(inputDir+os.sep + releaseDir+os.sep + '*.shp'))
    log.info('Release area files are: %s' % relFiles)

    # Initialise resistance areas
    resFile, entResInfo['flagRes'] = getAndCheckInputFiles(inputDir, 'RES', 'Resistance', fileExt='shp')
    if resFile is None:
        resFile = ''
    # Initialise entrainment areas
    entFile, entResInfo['flagEnt'] = getAndCheckInputFiles(inputDir, 'ENT', 'Entrainment', fileExt='shp')
    if entFile is None:
        entFile = ''
    # Initialise dam line
    wallFile, entResInfo['flagWall'] = getAndCheckInputFiles(inputDir, 'DAM', 'Dam', fileExt='shp')
    # Initialise DEM
    demFile = getDEMPath(avaDir)

    return demFile, relFiles, entFile, resFile, wallFile, entResInfo


def getInputDataCom1DFA(avaDir):
    """ Fetch input datasets required for simulation, duplicated function because
        now fetch all available files
        simulation type set differently in com1DFA compared to com1DFAOrig:
        TODO: remove duplicate once it is not required anymore

    Parameters
    ----------
    avaDir : str or pathlib object
        path to avalanche directory
    cfg : dict
        configuration read from com1DFA simulation ini file

    Returns
    -------
    inputSimFiles: dict
        dictionary with all the input files:
        demFile : str (first element of list)
            list of full path to DEM .asc file
        relFiles : list
            list of full path to release area scenario .shp files
        secondaryReleaseFile : str
            full path to secondary release area .shp file
        entFile : str
            full path to entrainment area .shp file
        resFile : str
            full path to resistance area .shp file
        entResInfo : flag dict
            flag if Yes entrainment and/or resistance areas found and used for simulation
            flag True if a Secondary Release file found and activated
    """

    # Set directories for inputs, outputs and current work
    inputDir = pathlib.Path(avaDir, 'Inputs')

    # Set flag if there is an entrainment or resistance area
    entResInfo = {}

    releaseDir = 'REL'
    releaseDir = inputDir / 'REL'
    relFiles = sorted(list(releaseDir.glob('*.shp')))
    log.info('Release area files are: %s' % [str(relFilestr) for relFilestr in relFiles])

    # check if relThFile is available
    relThFile, entResInfo['releaseThicknessFile'] = getAndCheckInputFiles(inputDir, 'RELTH',
                                                                          'release thickness data', fileExt='asc')

    # Initialise secondary release areas
    secondaryReleaseFile, entResInfo['flagSecondaryRelease'] = getAndCheckInputFiles(inputDir, 'SECREL',
                                                                                     'Secondary release', fileExt='shp')

    # Initialise resistance areas
    resFile, entResInfo['flagRes'] = getAndCheckInputFiles(inputDir, 'RES', 'Resistance', fileExt='shp')

    # Initialise entrainment areas
    entFile, entResInfo['flagEnt'] = getAndCheckInputFiles(inputDir, 'ENT', 'Entrainment', fileExt='shp')

    # Initialise dam line
    damFile, entResInfo['dam'] = getAndCheckInputFiles(inputDir, 'DAM', 'Dam', fileExt='shp')

    # Initialise DEM
    demFile = getDEMPath(avaDir)

    # return DEM, first item of release, entrainment and resistance areas
    inputSimFiles = {'demFile': demFile, 'relFiles': relFiles, 'secondaryReleaseFile': secondaryReleaseFile,
                     'entFile': entFile, 'resFile': resFile, 'damFile': damFile, 'entResInfo': entResInfo,
                     'relThFile': relThFile}

    return inputSimFiles


def getAndCheckInputFiles(inputDir, folder, inputType, fileExt='shp'):
    """Fetch fileExt files and check if they exist and if it is not more than one

    Raises error if there is more than one fileExt file.

    Parameters
    ----------
    inputDir : pathlib object or str
        path to avalanche input directory
    folder : str
        subfolder name where the shape file should be located (SECREL, ENT or RES)
    inputType : str
        type of input (used for the logging messages). Secondary release or Entrainment or Resistance
    fileExt: str
        file extension e.g. shp, asc - optional default is shp

    Returns
    -------
    OutputFile: str
        path to file checked
    available: str
        Yes or No depending of if there is a shape file available (if No, OutputFile is None)
    """
    available = 'No'
    # Initialise secondary release areas
    dir = pathlib.Path(inputDir, folder)
    OutputFile = list(dir.glob('*.%s' % fileExt))
    if len(OutputFile) < 1:
        OutputFile = None
    elif len(OutputFile) > 1:
        message = 'More than one %s .%s file in %s/%s/ not allowed' % (inputType, fileExt, inputDir, folder)
        log.error(message)
        raise AssertionError(message)
    else:
        available = 'Yes'
        OutputFile = OutputFile[0]

    return OutputFile, available


def getThicknessInputSimFiles(inputSimFiles, avaDir, modName):
    """ add thickness of shapefiles to dictionary

        Parameters
        -----------
        inputSimFiles: dict
            dictionary with info on release and entrainment file paths
        avaDir: str or pathlib path
            path to avalanche directory
        modName : computational module
            computational module

        Returns
        --------
        inputSimFiles: dict
            updated dictionary with thickness info read from shapefile attributes
            now includes one separate dictionary for each release, entrainment or secondary release
            scenario with a thickness and id value for each feature (given as list)
    """

    # create pathlib Path
    avaDir = pathlib.Path(avaDir)

    # check if thickness info is required from entrainment and secondary release according to simType
    thTypeList = ['entFile', 'secondaryReleaseFile']

    # fetch thickness attribute of entrainment area and secondary release
    for thType in ['entFile', 'secondaryReleaseFile']:
        if inputSimFiles[thType] != None:
            thicknessList, idList, ci95List = shpConv.readThickness(inputSimFiles[thType])
            inputSimFiles[inputSimFiles[thType].stem] = {'thickness': thicknessList, 'id': idList,
                'ci95': ci95List}

    # initialize release scenario list
    releaseScenarioList = []

    # fetch thickness attribute of release areas and add info to input dict
    for releaseA in inputSimFiles['relFiles']:
        # fetch thickness and id info from input data
        thicknessList, idList, ci95List = shpConv.readThickness(releaseA)
        inputSimFiles[releaseA.stem] = {'thickness': thicknessList, 'id': idList, 'ci95': ci95List}
        # append release scenario name to list
        releaseScenarioList.append(releaseA.stem)

    return inputSimFiles


def updateThicknessCfg(inputSimFiles, avaDir, modName, cfgInitial):
    """ add available release scenarios to ini file and
        set thickness values in ini files

        Parameters
        -----------
        inputSimFiles: dict
            dictionary with info on release and entrainment file paths
        avaDir: str or pathlib path
            path to avalanche directory
        modName : computational module
            computational module
        cfgInitial: configParser object
            configParser object with the current (and possibly overridden) configuration

        Returns
        --------
        inputSimFiles: dict
            updated dictionary with thickness info read from shapefile attributes
            now includes one separate dictionary for each release, entrainment or secondary release
            scenario with a thickness and id value for each feature (given as list)
        cfgInitial: configparser object
            updated config object with release scenario, thickness info, etc.

    """

    # create pathlib Path
    avaDir = pathlib.Path(avaDir)

    # get name of module as string
    modNameString = str(pathlib.Path(modName.__file__).stem)

    # check if thickness info is required from entrainment and secondary release according to simType
    simTypeList = cfgInitial['GENERAL']['simTypeList'].split('|')
    thTypeList = []
    if any(simType in ['ent', 'entres', 'available'] for simType in simTypeList):
        thTypeList.append('entFile')
    if cfgInitial['GENERAL'].getboolean('secRelArea'):
        thTypeList.append('secondaryReleaseFile')

    # initialize release scenario list
    releaseScenarioList = []

    # add input data info to cfg object
    # fetch thickness attribute of release areas and add info to input dict
    for releaseA in inputSimFiles['relFiles']:
        # append release scenario name to list
        releaseScenarioList.append(releaseA.stem)
        # update configuration with thickness value to be used for simulations
        cfgInitial = dP.getThicknessValue(cfgInitial, inputSimFiles, releaseA.stem, 'relTh')
        if cfgInitial['GENERAL'].getboolean('relThFromFile'):
            cfgInitial['INPUT']['relThFile'] = str(pathlib.Path('RELTH', inputSimFiles['relThFile'].name))

    # add entrainment and secondary release thickness in input data info and in cfg object
    if inputSimFiles['entFile'] != None and 'entFile' in thTypeList:
        cfgInitial = dP.getThicknessValue(cfgInitial, inputSimFiles, inputSimFiles['entFile'].stem, 'entTh')
        cfgInitial['INPUT']['entrainmentScenario'] = inputSimFiles['entFile'].stem
    if inputSimFiles['secondaryReleaseFile'] != None and 'secondaryReleaseFile' in thTypeList:
        cfgInitial = dP.getThicknessValue(cfgInitial, inputSimFiles,
            inputSimFiles['secondaryReleaseFile'].stem, 'secondaryRelTh')
        cfgInitial['INPUT']['secondaryReleaseScenario'] = inputSimFiles['secondaryReleaseFile'].stem

    # create cfg string from release scenario list and add to cfg object
    releaseScenarioName = cfgUtils.convertToCfgList(releaseScenarioList)
    if cfgInitial['INPUT']['releaseScenario'] == '':
        cfgInitial['INPUT']['releaseScenario'] = releaseScenarioName
    else:
        if cfgInitial['INPUT']['releaseScenario'] not in releaseScenarioList:
            message = ('Chosen release scenario: %s not available' % cfgInitial['INPUT']['releaseScenario'])
            log.error(message)
            raise FileNotFoundError(message)
        else:
            log.info('Chosen release scenarios: %s' % cfgInitial['INPUT']['releaseScenario'])

    return cfgInitial


def initializeDEM(avaDir, demPath=''):
    """ check for dem and load to dict

        Parameters
        -----------
        avaDir: str or pathlib path
            path to avalanche directory
        demPath: str or pathlib Path
            path to dem relative to Inputs - optional if not provided read DEM from Inputs

        Returns
        --------
        demOri: dict
            dem dictionary with header and data
    """

    if demPath == '':
        dem = readDEM(avaDir)
    else:
        # build full path and load data to dict
        demFile = pathlib.Path(avaDir, 'Inputs', demPath)
        dem = IOf.readRaster(demFile, noDataToNan=True)

    return dem


def selectReleaseFile(inputSimFiles, releaseScenario):
    """ select release scenario

        Parameters
        -----------
        inputSimFiles: dict
            dictionary with info on input data
        releaseScenario: str
            name of release scenario


        Returns
        -------
        inputSimFiles: dict
            dictionary with info on input data updated with releaseScenario
    """


    # fetch release file path for scenario
    relFiles = inputSimFiles['relFiles']
    for relF in relFiles:
        if relF.stem == releaseScenario:
            releaseScenarioPath = relF

    inputSimFiles['releaseScenario'] =  releaseScenarioPath

    return inputSimFiles


def fetchReleaseFile(inputSimFiles, releaseScenario, cfgSim, releaseList):
    """ select release scenario, update configuration to only include thickness info
        of current scenario and return file path

        Parameters
        -----------
        inputSimFiles: dict
            dictionary with info on input data
        releaseScenario: str
            name of release scenario
        cfgSim: conigparser object
            configuration of simulation
        releaseList: list
            list of available release scenarios

        Returns
        -------
        releaseScenarioPath: pathlib path
            file path to release scenario shp file
        cfgSim: configparser object
            updated cfg object, removed thickness info from not other release scenarios than used
            one and rename thickness values of chosen scenario to relThThickness, relThId, ...
    """

    # fetch release files paths
    relFiles = inputSimFiles['relFiles']

    foundScenario = False
    for relF in relFiles:
        if relF.stem == releaseScenario:
            releaseScenarioPath = relF
            foundScenario = True

    if foundScenario is False:
        message = 'Release area scenario %s not found - check input data' % (releaseScenario)
        log.error(message)
        raise FileNotFoundError(message)

    # update config entry for release scenario, thickness and id
    cfgSim['INPUT']['releaseScenario'] = str(releaseScenario)
    if cfgSim['GENERAL']['relThFromShp'] == 'True':
        for scenario in releaseList:
            if scenario == releaseScenario:
                cfgSim['INPUT']['relThId'] = cfgSim['INPUT'][scenario + '_' + 'relThId']
                cfgSim['INPUT']['relThThickness'] = cfgSim['INPUT'][scenario + '_' + 'relThThickness']
                cfgSim['INPUT']['relThCi95'] = cfgSim['INPUT'][scenario + '_' + 'relThCi95']
            # remove thickness, id and ci95 values specified by releaseScenario
            cfgSim['INPUT'].pop(scenario + '_' + 'relThId')
            cfgSim['INPUT'].pop(scenario + '_' + 'relThThickness')
            cfgSim['INPUT'].pop(scenario + '_' + 'relThCi95')

    return releaseScenarioPath, cfgSim
