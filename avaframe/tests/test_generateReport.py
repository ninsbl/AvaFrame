"""
    Pytest for getReleaseArea

    This file is part of Avaframe.

 """

#  Load modules
import numpy as np
import os
from avaframe.log2Report import generateReport as gR

import pytest
import configparser


def test_writeReport():
    """ Test generation markdown report file """

    # Initialise input dictionary
    testDict = {'title info' : {'name' : 'This is my report title', 'type' : 'title',
                'testNo' : 'this should not appear in the report if working fine!'},
        'simName': {'type' : 'simName', 'name' : 'this is my simulation name'},
        'Testing Parameters': {'release area': 'release1HS2', 'Mu': '0.155', 'type' : 'list'},
        'Release area': {'release area scenario': 'my test release area', 'type' : 'columns'},
        'Special Input': {'Additional snow-covered area': 'Area 1', 'type' : 'columns'},
        'Additional Info' : {'type' : 'text', 'Report Info' : 'This simulations were performed with a developement version.'},
        'Fancy plots' : {'type' : 'image', 'Peak Pressure Field of my test' : 'release1HS2_entres_dfa_0.750_pfd.png'}}

    # make a list of input dictionaries
    reportDictList = [testDict]

    testDir = os.path.join(os.getcwd(), 'avaframe', 'tests')
    # Call function to be tested
    gR.writeReport(testDir, reportDictList, reportOneFile=True)

    # Load simulation report
    reportFile = open(os.path.join(testDir, 'fullSimulationReport.md'), 'r')
    lines = reportFile.readlines()
    lineVals = []
    for line in lines:
        lineVals.append(line)

    # Test
    assert lineVals[0] == '# This is my report title \n'
    assert lineVals[4] == '| ---------- | ------ | \n'
    assert lineVals[5] == '| release area | release1HS2 | \n'
    assert lineVals[14] == '| Additional snow-covered area | \n'
    assert lineVals[15] == '| ----------| \n'
    assert lineVals[-1] == '![Peak Pressure Field of my test](release1HS2_entres_dfa_0.750_pfd.png) \n'
