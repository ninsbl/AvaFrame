"""
    Conversion functions to read/ write Shape files or xyz profiles
"""


import os
import shapefile
import sys
import copy
import numpy as np
import logging

# create local logger
log = logging.getLogger(__name__)


def SHP2Array(infile, defname=None):
    """ Read shapefile and convert it to a python dictionnary
    containing the name of the paths in the shape file, the np array with
    the coordinates of the path points (all stacked in the same array)
    and information about the startin index and length of each path
    Output : SHPdata dictionnary
    SHPdata['Name'] = list of paths names
    SHPdata['Coord'] = np array of the coords of points in paths
    SHPdata['Start'] = list of starting index of each path in Coord
    SHPdata['Length'] = list of length of each path in Coord
    """
    #  Input shapefile
    sf = shapefile.Reader(infile)

    # set defaults for variables
    layername = None
    d0 = None
    rho = None
    sks = None
    iso = None
    d01 = []

    # get coordinate system
    prjfile = infile.replace('.shp', '.prj')
    if os.path.isfile(prjfile):
        prjf = open(prjfile, 'r')
        sks = prjf.readline()

    # Start reading the shapefile
    records = sf.shapeRecords()
    shps = sf.shapes()

    SHPdata = {}
    SHPdata['sks'] = sks
    Name = []
    Length = np.empty((0))
    Start = np.empty((0))
    Coordx = np.empty((0))
    Coordy = np.empty((0))
    Coordz = np.empty((0))
    start = 0

    for n, item in enumerate(shps):
        pts = item.points
        zs = [0.0] * len(pts)

        # check if records are available and extract
        if records:
            # loop through fields
            for (name, typ, size, deci), value in zip(sf.fields[1:], records[n].record):
                # get entity name
                name = name.lower()
                if (name == 'name'):
                    layername = str(value)
                if (name == 'd0'):
                    d0 = value
                if (name == 'rho'):
                    rho = value
                if (name == 'sks'):
                    sks = value
                if (name == 'iso'):
                    iso = value
            # if name is still empty go through file again and take Layer instead
            if ((type(layername) is bytes) or (layername is None)):
                for (name, typ, size, deci), value in zip(sf.fields[1:], records[n].record):
                    if (name == 'Layer'):
                        layername = value

        # if layer still not defined, use generic
        if layername is None:
            layername = defname

        Name.append(layername)
        log.debug('SHPConv: Found layer %s', layername)
        d01.append(str(d0))

        Start = np.append(Start, start)
        length = len(pts)
        Length = np.append(Length, length)
        start += length

        for (pt, z) in zip(pts, zs):
            Coordx = np.append(Coordx, pt[0])
            Coordy = np.append(Coordy, pt[1])
            Coordz = np.append(Coordz, z)

    SHPdata['Name'] = Name
    SHPdata['d0'] = d01
    SHPdata['Start'] = Start
    SHPdata['Length'] = Length
    SHPdata['x'] = Coordx
    SHPdata['y'] = Coordy
    SHPdata['z'] = Coordz
    return SHPdata


def readLine(fname, defname, dem):
    """ Read avalanche path from  .shp"""

    log.debug('Reading avalanche path : %s ', fname)
    header = dem['header']
    rasterDEM = dem['rasterData']
    Line = SHP2Array(fname, defname)
    coordx = Line['x']
    coordy = Line['y']
    for i in range(len(coordx)):
        Lx = (coordx[i] - header.xllcenter) / header.cellsize
        Ly = (coordy[i] - header.yllcenter) / header.cellsize
        if ((Ly < 0) or (Ly > header.nrows-1) or (Lx < 0) or (Lx > header.ncols-1)):
            raise ValueError('The avalanche path exceeds dem extent. Try with another path')
        elif np.isnan(rasterDEM[int(np.floor(Ly)), int(np.floor(Lx))]):
            raise ValueError('Nan Value encountered. Try with another path')
    return Line


def readPoints(fname, dem):
    """ Read split point path from .shp"""

    log.debug('Reading split point : %s ', fname)
    header = dem['header']
    rasterDEM = dem['rasterData']
    defname = 'SHP'
    Points = SHP2Array(fname, defname)
    Pointx = Points['x']
    Pointy = Points['y']
    for i in range(len(Pointx)):
        Lx = (Pointx[i] - header.xllcenter) / header.cellsize
        Ly = (Pointy[i] - header.yllcenter) / header.cellsize
        if (Ly < 0 or Ly > header.nrows-1 or Lx < 0 or Lx > header.ncols-1):
            raise ValueError('The split point is not on the dem. Try with another split point')
        elif np.isnan(rasterDEM[int(np.floor(Ly)), int(np.floor(Lx))]):
            raise ValueError('Nan Value encountered. Try with another split point')
    return Points


def removeFeature(featureIn, featureName):
    """ Remove feature featureName from featureIn"""
    NameRel = featureIn['Name']
    StartRel = featureIn['Start']
    LengthRel = featureIn['Length']
    d0 = featureIn['d0']
    featureOut = copy.deepcopy(featureIn)
    # find index of feature to remove
    nFeature2Remove = NameRel.index(featureName)
    start = StartRel[nFeature2Remove]
    end = start + LengthRel[nFeature2Remove]
    # remove feature
    featureOut['x'] = np.delete(featureIn['x'], np.arange(int(start), int(end)))
    featureOut['y'] = np.delete(featureIn['y'], np.arange(int(start), int(end)))
    del NameRel[nFeature2Remove]
    featureOut['Name'] = NameRel
    StartRel = StartRel[nFeature2Remove:] - LengthRel[nFeature2Remove]
    featureOut['Start'] = np.delete(StartRel, nFeature2Remove)
    featureOut['Length'] = np.delete(LengthRel, nFeature2Remove)
    featureOut['d0'] = np.delete(d0, nFeature2Remove)

    return featureOut


def extractFeature(featureIn, featureName):
    """ Extract feature featureName from featureIn"""
    NameRel = featureIn['Name']
    StartRel = featureIn['Start']
    LengthRel = featureIn['Length']
    d0 = featureIn['d0']
    featureOut = copy.deepcopy(featureIn)
    # find index of feature to extract
    nFeature2Extract = NameRel.index(featureName)
    # extract feature
    featureOut['Name'] = [NameRel[nFeature2Extract]]
    featureOut['Start'] = np.array([StartRel[nFeature2Extract]])
    featureOut['Length'] = np.array([LengthRel[nFeature2Extract]])
    featureOut['d0'] = np.array([d0[nFeature2Extract]])
    start = StartRel[nFeature2Extract]
    end = start + LengthRel[nFeature2Extract]
    featureOut['x'] = featureIn['x'][int(start):int(end)]
    featureOut['y'] = featureIn['y'][int(start):int(end)]

    return featureOut
