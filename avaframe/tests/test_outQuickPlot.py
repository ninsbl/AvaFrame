"""
    Pytest for module outQuickPlot

 """

#  Load modules
import numpy as np
import os
from avaframe.out3Plot import outQuickPlot as oP
from avaframe.in3Utils import cfgUtils
from avaframe.in3Utils import fileHandlerUtils as fU
import pytest
import configparser
import shutil
import pathlib


def test_generatePlot(tmp_path):

    # Initialise inputs
    avaName = 'avaHockeyChannel'
    avaTestDir = 'avaPlotPytest'
    dirPath = pathlib.Path(__file__).parents[0]
    avaDir = dirPath / '..' / '..' / 'benchmarks' / avaTestDir
    outDir = tmp_path

    data1File = avaDir / 'release1HS_entres_ref_0.15500_pfd.asc'
    data2File = avaDir / 'release2HS_entres_ref_0.15500_pfd.asc'
    data1 = np.loadtxt(data1File, skiprows=6)
    data2 = np.loadtxt(data2File, skiprows=6)
    cellSize = 5.
    cfg = configparser.ConfigParser()
    cfg['FLAGS'] = {'showPlot': False}

    dataDict = {'data1': data1, 'data2': data2, 'name1': 'release1HS_entres_ref_0.15500_pfd',
                'name2': 'release2HS_entres_ref_0.15500_pfd.asc', 'compareType': 'compToRef',
                'simName': 'release1HS_entres_ref_0.15500', 'suffix': 'pfd', 'cellSize': cellSize, 'unit': 'm'}

    # Initialise plotList
    rel = 'release1HS'
    plotDict = {'relArea' : rel, 'plots': [], 'difference': [], 'differenceZoom': [], 'stats': []}
    plotDictNew = oP.generatePlot(dataDict, avaName, outDir, cfg, plotDict)


    assert (plotDict['difference'][0] == 4.0)
    assert (plotDict['difference'][1] == -0.5)
    assert (plotDict['difference'][2] == -8.0)
    assert (plotDict['differenceZoom'][0] == 0)
    assert (plotDict['differenceZoom'][1] == -0.023255813953488372)
    assert (plotDict['differenceZoom'][2] == -1.0)


def test_quickPlotSimple(tmp_path):
    """ test generating a comparison plot of two raster datasets """

    # setup required input
    testDir = pathlib.Path(__file__).parents[0]
    inputDir = testDir / '..' / '..' / 'benchmarks' / 'avaPlotPytest'
    avaDir = pathlib.Path(tmp_path, 'avaPlots')
    shutil.copytree(inputDir, avaDir)

    cfg = configparser.ConfigParser()
    cfg['FLAGS'] = {'showPlot': 'False'}

    plotDict = oP.quickPlotSimple(avaDir, avaDir, cfg)

    assert (plotDict['difference'][0] == 4.0)
    assert (plotDict['difference'][1] == -0.5)
    assert (plotDict['difference'][2] == -8.0)


def test_quickPlotBench(tmp_path):
    """ test generating a comparison plot of two raster datasets """

    # setup required input
    testDir = pathlib.Path(__file__).parents[0]
    inputDir = testDir / '..' / '..' / 'benchmarks' / 'avaPlotPytest'
    refDir = pathlib.Path(tmp_path, 'reference')
    compDir = pathlib.Path(tmp_path, 'comparison')
    avaDir = pathlib.Path(tmp_path, 'avaBench')
    fU.makeADir(refDir)
    fU.makeADir(compDir)
    fU.makeADir(avaDir)
    simNameRef = 'release1HS_entres_ref_0.15500'
    simNameComp = 'release2HS_entres_ref_0.15500'

    refFile = inputDir / (simNameRef + '_pfd.asc')
    simFile = inputDir / (simNameComp + '_pfd.asc')
    refFileTest = refDir / (simNameRef + '_pfd.asc')
    simFileTest = compDir / (simNameComp + '_pfd.asc')

    shutil.copy(refFile, refFileTest)
    shutil.copy(simFile, simFileTest)

    cfg = configparser.ConfigParser()
    cfg['FLAGS'] = {'showPlot': 'False'}
    suffix = 'pfd'

    # call function to be tested
    plotDict = oP.quickPlotBench(avaDir, simNameRef, simNameComp, refDir, compDir, cfg, suffix)

    testPath = avaDir / 'Outputs' / 'out3Plot' / ('Diff_avaBench_%s_pfd.png' % simNameComp)

    assert (plotDict['difference'][0] == 8.0)
    assert (plotDict['difference'][1] == 0.5)
    assert (plotDict['difference'][2] == -4.0)
    assert plotDict['plots'][0] == testPath
    assert plotDict['stats'][0] == 10.
    assert plotDict['stats'][1] == 0.
