''' Tests for module distanceTimeAnalysis  '''
import numpy as np
import numpy.ma as ma
import pandas as pd
import pathlib
import configparser
import matplotlib.pyplot as plt

# Local imports
import avaframe.ana5Utils.distanceTimeAnalysis as dtAna
import avaframe.in2Trans.ascUtils as IOf
from avaframe.in3Utils import cfgUtils


def test_getRadarLocation():
    """ test get radar location """

    # setup required inputs
    cfg = configparser.ConfigParser()
    cfg['GENERAL'] = {'radarLocation': '10.|25.|40.|57.'}

    # call function to be tested
    radarFov = dtAna.getRadarLocation(cfg)

    assert radarFov[0][0] == 10.
    assert radarFov[1][1] == 57.
    assert np.array_equal(radarFov, np.asarray([[10., 25.],[40., 57.]]))


def test_setDEMOrigin():
    """ test setting of DEM origin back to original """

    # setup required inputs
    headerDEM = {'xllcenter': 0.0, 'yllcenter': 0.0, 'cellsize': 2., 'ncols': 8, 'nrows': 11}
    demSims = {'header': headerDEM, 'originalHeader': {'xllcenter': 1.0, 'yllcenter': 5.,
        'cellsize': 2., 'ncols': 8, 'nrows': 11},
        'rasterData': np.zeros((11, 8))}

    # call function to be tested
    demOriginal = dtAna.setDemOrigin(demSims)

    assert demOriginal['header']['xllcenter'] == 1.0
    assert demOriginal['header']['yllcenter'] == 5.0
    assert demOriginal['header']['ncols'] == 8
    assert demOriginal['header']['nrows'] == 11
    assert demOriginal['header']['cellsize'] == 2.


def test_radarMask(tmp_path):
    """ test creating radar mask array """

    # setup required input
    testAvaDir = pathlib.Path(tmp_path, 'testAva')
    headerDEM = {'xllcenter': 0.0, 'yllcenter': 0.0, 'cellsize': 1., 'ncols': 11, 'nrows': 11}
    demOriginal = {'header': headerDEM, 'rasterData': np.zeros((11, 11))}
    radarFov = [[1., 10.0], [5., 5.]]
    aperture = 40.5
    cfgRangeTime = configparser.ConfigParser()
    cfgRangeTime['GENERAL'] = {'rgWidth': 2., 'avalancheDir': testAvaDir, 'simHash': 'test123',
        'gateContours': 20}

    # call function to be tested
    radarRange, rangeGates = dtAna.radarMask(demOriginal, radarFov, aperture, cfgRangeTime)

    print('randarRange', radarRange)
    print('rangeGates', rangeGates)


    assert np.array_equal(rangeGates, np.asarray([2., 4., 6., 8., 10., 12.]))


def setupRangeTimeDiagram():
    """ test setting up range time diagram """

    # setup required inputs
    headerDEM = {'xllcenter': 0.0, 'yllcenter': 0.0, 'cellsize': 1., 'ncols': 11, 'nrows': 11}
    demOriginal = {'header': headerDEM, 'rasterData': np.zeros((11, 11))}

    cfgRangeTime = configparser.ConfigParser()
    cfgRangeTime['GENERAL'] = {'rgWidth': 2., 'avalancheDir': testAvaDir, 'simHash': 'test123',
        'gateContours': 20, 'aperture': 40.5}

    # call function to be tested
    mtiInfo = dtAna.setupRangeTimeDiagram(demOriginal, cfgRangeTime)

    assert np.array_equal(mtiInfo['rangeGates'], np.asarray([2., 4., 6., 8., 10., 12.]))

# def test_minRangeSimulation():
#     """ test if min range is found in simulation results """
#
#     # setup required inputs
#     flowF = np.zeros((10, 12))
#     flowF[4,4:6] = 4.5
#     flowF[5,4:6] = 4.2
#     threshold = 4.19
#     rangeMasked = np.arange(12)
#     rangeMasked = np.repeat([rangeMasked], 10, axis=0)
#
#     # call function to be tested
#     losRange = dtAna.minRangeSimulation(flowF, rangeMasked, threshold)
#
#     assert losRange == 4.


def test_appraoachVelocity():
    """ test computing approach velocity """

    # setup required inputs
    mtiInfo = {'timeList': [0., 2., 3., 7., 8., 9., 10.],
        'rangeList': [0., 2., 4., 6., 8., 10., 12]}
    minVelTimeStep = 2.

    # call function to be tested
    maxVel, rangeVel, timeVel = dtAna.approachVelocity(mtiInfo, minVelTimeStep)

    assert maxVel == 2.
    assert rangeVel == 8.
    assert timeVel == 8.

def test_fetchTimeStepFromName():
    """ test fetching time step from name """

    # setup required inpu
    pathNames = pathlib.Path('tests', 'testName_t0.5.asc')

    # call function to be tested
    timeSteps, indexTime = dtAna.fetchTimeStepFromName(pathNames)

    assert timeSteps == [0.5]
    assert indexTime == [0]

    # setup required inpu
    pathNames = [pathlib.Path('tests', 'testName_t0.5.asc'),
        pathlib.Path('tests', 'testName_t0.15.asc')]

    # call function to be tested
    timeSteps, indexTime = dtAna.fetchTimeStepFromName(pathNames)

    assert timeSteps == [0.5, 0.15]
    assert indexTime[0] == 1
    assert indexTime[1] == 0


def test_importMTIData():
    """ testing importing data pickle """

    # setup required inputs
    dirPath = pathlib.Path(__file__).parents[0]
    avaDir = 'data/avaTest'
    modName = 'com1DFA'
    inputDir = dirPath / 'data' / 'avaTest'
    simHash = 'simTestID'

    # call function to be tested
    mtiInfoDicts = dtAna.importMTIData(avaDir, modName, inputDir=inputDir)

    assert len(mtiInfoDicts) == 2

    # call function to be tested
    mtiInfoDicts2 = dtAna.importMTIData(avaDir, modName, inputDir=inputDir, simHash=simHash)

    assert len(mtiInfoDicts2) == 1
    assert mtiInfoDicts2[0]['name'] == (inputDir / 'testpickle_simTestID.p')


def test_exportData(tmp_path):
    """ test exporting pickle """

    # setup require inputs
    mtiInfo = {'name': 'testName', 'testArray': np.arange(10)}
    cfg = configparser.ConfigParser()
    testDir = pathlib.Path(tmp_path)
    cfg['GENERAL'] = {'avalancheDir': testDir, 'simHash': 'simTestID'}
    modName = 'com1DFA'

    # call function to be tested
    dtAna.exportData(mtiInfo, cfg, modName)

    testPath = testDir / 'Outputs' / modName / 'distanceTimeAnalysis' / 'mtiInfo_simTestID.p'
    assert testPath.is_file()


def test_maskRangeFull():
    """ test creating full mask """

    # setup required input parameters
    flowF = np.asarray([[2., 2., 2., 2.],
                        [3., 4., 5., 6.],
                        [7., 2., 0., 0.],
                        [6., 7., 8., 10.],
                        [2., 4., 5., 7.]])
    threshold = 3.1
    range = np.arange(4)
    range = np.repeat([range], 5, axis=0)
    rangeMasked = np.ma.masked_where(range < 2., range)

    # call function to be tested
    maskAva, maskFull, maskFullRange = dtAna.maskRangeFull(flowF, threshold, rangeMasked)
    maskSol = np.asarray([[True, True, True, True],
                          [True, True, False, False],
                          [True, True, True, True],
                          [True, True, False, False],
                          [True, True, False, False]])
    maskAvaSol = np.asarray([[True, True, True, True],
                          [True, False, False, False],
                          [False, True, True, True],
                          [False, False, False, False],
                          [True, False, False, False]])

    assert np.array_equal(maskSol, maskFull)
    assert np.array_equal(maskAvaSol, maskAva.mask)

def test_extractFrontAndMeanValuesRadar():
    """ test extracting front and mean values """

    # setup required input
    cfgRangeTime = configparser.ConfigParser()
    cfgRangeTime['GENERAL'] = {'rgWidth': 2., 'thresholdResult': 3.1}
    cfgRangeTime['PLOTS'] = {'debugPlot': False}
    flowF = np.asarray([[2., 2., 2., 2.],
                        [3., 4., 5., 6.],
                        [7., 2., 0., 0.],
                        [6., 7., 8., 10.],
                        [2., 4., 5., 7.]])
    threshold = 3.1
    range = np.arange(4)
    range = np.repeat([range], 5, axis=0)
    rangeMasked = np.ma.masked_where(range < 2., range)
    mtiInfo = {'rangeGates': np.arange(4), 'rangeMasked': rangeMasked, 'rArray': range,
    'mti': np.zeros(5), 'rangeList': [], 'timeList': []}

    # call function to be tested
    mtiInfo = dtAna.extractFrontAndMeanValuesRadar(cfgRangeTime, flowF, mtiInfo)
    print('mtiInfo', mtiInfo)

    assert mtiInfo['timeList'] == []
    assert mtiInfo['rangeList'] == [2]
    assert mtiInfo['mti'][0] == 0
    assert mtiInfo['mti'][1] == 0
    assert mtiInfo['mti'][2] == 6.
    assert mtiInfo['mti'][3] == 23./3
