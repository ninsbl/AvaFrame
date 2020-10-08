"""Tests for module logUtilis"""
import avaframe.in3Utils.logUtils as logUtils
from avaframe.in3Utils import cfgUtils
from avaframe.tests import test_logUtils
import os


def test_initiateLogger(capfd):
    '''Simple test for module initiateLogger'''
    dirname = os.path.dirname(__file__)
    avalancheDir = dirname
    logName = 'testCFG'
    logUtils.initiateLogger(avalancheDir, logName)
    logFileName = os.path.join(avalancheDir, 'testCFG.log')
    assert os.path.isfile(logFileName)
    os.remove(logFileName)


def test_writeCfg2Log(capfd):
    '''Simple test for module writeCfg2Log'''
    dirname = os.path.dirname(__file__)
    avalancheDir = dirname
    logName = 'testCFG'
    logUtils.initiateLogger(avalancheDir, logName)
    cfg = cfgUtils.getModuleConfig(test_logUtils)
    logUtils.writeCfg2Log(cfg, 'test config')

    logFileName = os.path.join(avalancheDir, 'testCFG.log')
    logFileNameRef = os.path.join(avalancheDir, 'data', 'testCFGRef.tog')
    f = open(logFileName).readlines()
    for i in range(8):
        firstLine = f.pop(0)

    fref = open(logFileNameRef).readlines()
    os.remove(logFileName)
