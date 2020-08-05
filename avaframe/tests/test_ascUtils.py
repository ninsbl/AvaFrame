"""Tests for module com2AB"""
import numpy as np
import math
import pytest
import avaframe.in3Utils.ascUtils as IOf
import unittest
import os


def test_readASCheader(capfd):
    '''Simple test for module readASCheader'''
    dirname = os.path.dirname(__file__)
    DGMSource = os.path.join(dirname, '../data/avaSlide/slideTopo.asc')
    header = IOf.readASCheader(DGMSource)
    print(header.ncols)
    assert((header.ncols == 419) and (header.nrows == 201) and
           (header.cellsize == 5))


def test_readASCdata2numpyArray(capfd):
    '''Simple test for module readASCheader'''
    dirname = os.path.dirname(__file__)
    DGMSource = os.path.join(dirname, '../data/avaSlide/slideTopo.asc')
    data = IOf.readASCdata2numpyArray(DGMSource)

    assert((data[0][0] == 1752.60) and (data[2][1] == 1749.10)
           and (data[0][3] == 1742.10))
