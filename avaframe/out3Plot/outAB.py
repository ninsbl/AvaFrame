"""
    Plotting and saving Alpha Beta results
"""

import pickle
import pathlib
import logging
import copy
import datetime
import shapefile
import matplotlib
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.axes_grid1 import make_axes_locatable

matplotlib.use('agg')

# Local imports
import avaframe.out3Plot.plotUtils as pU

# create local logger
log = logging.getLogger(__name__)

colors = ["#393955", "#8A8A9B", "#E9E940"]
mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=colors)


def writeABtoSHP(pathDict, resAB):
    """ Write com2AB results to shapefile

    Parameters
    ----------
    pathDict : dict
        dictionary with saveOutPath (path to output directory)
    resAB : dict
        dict with com2AB results

    Returns
    -------
    saveOutFile: str
        path to shapefile
    """

    saveOutFile = pathlib.Path(pathDict['saveOutPath']) / 'com2AB_Results'

    # open shapefile writer with point shapetype
    w = shapefile.Writer(str(saveOutFile), shapeType=1)

    # set fields
    w.field('fid', 'N')
    w.field('Name', 'C', '60')
    w.field('Angle', 'F', 5, 1)

    # loop through the profiles
    for i, profileName in enumerate(resAB):
        cuProf = resAB[profileName]

        pointName = profileName + '_Beta'
        w.point(cuProf['x'][cuProf['indBetaPoint']], cuProf['y'][cuProf['indBetaPoint']])
        w.record(i, pointName, cuProf['beta'])

        if cuProf['indAlpha'] is not None:
            pointName = profileName + '_Alpha'
            w.point(cuProf['x'][cuProf['indAlpha']], cuProf['y'][cuProf['indAlpha']])
            w.record(i, pointName, cuProf['alpha'])

        if cuProf['indAlphaP1SD'] is not None:
            pointName = profileName + '_AlphaPlus1SD'
            w.point(cuProf['x'][cuProf['indAlphaP1SD']], cuProf['y'][cuProf['indAlphaP1SD']])
            w.record(i, pointName, cuProf['alphaSD'][0])

        if cuProf['indAlphaM1SD'] is not None:
            pointName = profileName + '_AlphaMinus1SD'
            w.point(cuProf['x'][cuProf['indAlphaM1SD']], cuProf['y'][cuProf['indAlphaM1SD']])
            w.record(i, pointName, cuProf['alphaSD'][1])

        if cuProf['indAlphaM2SD'] is not None:
            pointName = profileName + '_AlphaMinus2SD'
            w.point(cuProf['x'][cuProf['indAlphaM2SD']], cuProf['y'][cuProf['indAlphaM2SD']])
            w.record(i, pointName, cuProf['alphaSD'][2])
    w.close()
    # write projection information file
    with open(str(saveOutFile)+'.prj', 'w') as prjf:
        prjf.write(cuProf['sks'])
    log.info('Writing com2AB to shapefile: %s.shp', saveOutFile)

    return saveOutFile


def readABresults(saveOutPath, name, flags):
    """ read the results generated by com2AB """
    savename = name + '_com2AB_eqparam.pickle'
    save_file = pathlib.Path(saveOutPath, savename)
    with open(save_file, 'rb') as handle:
        eqParams = pickle.load(handle)
    if not flags.getboolean('fullOut'):
        save_file.unlink()
    savename = name + '_com2AB_avaProfile.pickle'
    save_file = pathlib.Path(saveOutPath, savename)
    with open(save_file, 'rb') as handle:
        avaProfile = pickle.load(handle)
    if not flags.getboolean('fullOut'):
        save_file.unlink()

    return eqParams, avaProfile


def writeABpostOut(pathDict, dem, splitPoint, eqParams, resAB, cfgMain, reportDictList):
    """ Loops on the given Avapath, runs AlpahBeta Postprocessing
    plots Results and Write Results
    """
    saveOutPath = pathDict['saveOutPath']
    flags = cfgMain['FLAGS']
    FileNamePlot_ext = [None] * len(resAB.keys())
    FileNameWrite_ext = [None] * len(resAB.keys())
    for i, name in enumerate(resAB):
        avaProfile = resAB[name]
        # Plot the whole profile with beta, alpha ... points and lines
        plotPath(avaProfile, dem, splitPoint, flags)
        FileNamePlot_ext[i] = plotProfile(avaProfile, eqParams, saveOutPath)
        reportAB, FileNameWrite_ext[i] = WriteResults(avaProfile, eqParams, saveOutPath)
        reportAB['AlphaBeta plots'][name] = FileNamePlot_ext[i]
        # Add to report dictionary list
        reportDictList.append(reportAB)
    return reportDictList, FileNamePlot_ext, FileNameWrite_ext


def plotPath(avaProfile, dem, splitPoint, flags):
    """ Plot and save results depending on flags options"""
    header = dem['header']
    rasterdata = dem['rasterData']
    x = avaProfile['x']
    y = avaProfile['y']
    indSplit = avaProfile['indSplit']

    if flags.getboolean('debugPlot'):
        # Plot raster and path
        fig, ax = plt.subplots(figsize=(pU.figW, pU.figH))
        titleText = avaProfile['name']
        plt.title(titleText)
        cmap = copy.copy(mpl.cm.get_cmap("Greys"))
        cmap.set_bad(color='white')
        im = plt.imshow(rasterdata, cmap, origin='lower')
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)
        fig.colorbar(im, cax=cax)
        ax.plot((x-header['xllcenter'])/header['cellsize'],
                (y-header['yllcenter'])/header['cellsize'], 'k',
                label='avapath')
        ax.plot((splitPoint['x']-header['xllcenter'])/header['cellsize'],
                (splitPoint['y']-header['yllcenter'])/header['cellsize'], '.',
                color='0.3', label='Split points')
        ax.plot((x[indSplit]-header['xllcenter'])/header['cellsize'],
                (y[indSplit]-header['yllcenter'])/header['cellsize'], '.',
                color='0.6', label='Projection of Split Point on ava path')
        fig.legend(frameon=False, loc='lower center')
        pU.putAvaNameOnPlot(ax, avaProfile['name'])
        plt.show()


def plotProfile(avaProfile, eqParams, saveOutPath):
    """ Plot and or save profile results depending on plotting options"""
    s = avaProfile['s']
    z = avaProfile['z']
    indBetaPoint = avaProfile['indBetaPoint']
    poly = avaProfile['poly']
    beta = avaProfile['beta']
    alpha = avaProfile['alpha']
    f = avaProfile['f']
    indAlphaM1SD = avaProfile['indAlphaM1SD']
    indAlphaM2SD = avaProfile['indAlphaM2SD']
    indSplit = avaProfile['indSplit']
    parameterSet = eqParams['parameterSet']
    # Plot the whole profile with beta, alpha ... points and lines
    fig = plt.figure(figsize=(1.5*pU.figW, 1*pU.figH))
    titleText = avaProfile['name']
    plt.title(titleText)
    xlabelText = 'Distance [m]\nBeta: ' + str(round(beta, 1)) + \
        '°' + '  Alpha: ' + str(round(alpha, 1)) + '°'
    plt.xlabel(xlabelText, multialignment='center')
    plt.ylabel('Height [m]')
    plt.plot(s, z, '-', label='DEM')
    plt.plot(s, poly(s), ':', label='QuadFit')
    plt.axvline(x=s[indSplit], color='0.7',
                linewidth=1, linestyle='--', label='Split point')
    plt.axvline(x=s[indBetaPoint], color='0.8',
                linewidth=1, linestyle='-.', label='Beta')
    plt.plot(s, f, '-', label='AlphaLine')
    if indAlphaM1SD:
        plt.plot(s[indAlphaM1SD], z[indAlphaM1SD], 'x', markersize=8,
                 label='Alpha - 1SD')
    if indAlphaM2SD:
        plt.plot(s[indAlphaM2SD], z[indAlphaM2SD], 'x', markersize=8,
                 label='Alpha - 2SD')

    ax = plt.gca()
    fig.tight_layout()
    versionText = datetime.datetime.now().strftime("%d.%m.%y") + \
        '; ' + 'AlphaBeta ' + parameterSet
    plt.text(00, 0, versionText, fontsize=8, verticalalignment='bottom',
             horizontalalignment='left', transform=ax.transAxes,
             color='0.5')
    # plt.text(-0.2, 0, 'matplotlib -2', \
    #          verticalalignment='center', transform=ax.transAxes)

    plt.gca().set_aspect('equal', adjustable='box')
    plt.grid(linestyle=':', color='0.9')
    plt.legend(frameon=False)
    savename = avaProfile['name'] + '_AlphaBeta'
    outputFileName = pU.saveAndOrPlot({'pathResult': saveOutPath}, savename, fig)

    return outputFileName


def WriteResults(avaProfile, eqParams, saveOutPath):
    """ Write AB results to file """
    name = avaProfile['name']
    s = avaProfile['s']
    x = avaProfile['x']
    y = avaProfile['y']
    z = avaProfile['z']
    indBetaPoint = avaProfile['indBetaPoint']
    beta = avaProfile['beta']
    alpha = avaProfile['alpha']
    alphaSD = avaProfile['alphaSD']
    indAlpha = avaProfile['indAlpha']
    indAlphaP1SD = avaProfile['indAlphaP1SD']
    indAlphaM1SD = avaProfile['indAlphaM1SD']
    indAlphaM2SD = avaProfile['indAlphaM2SD']
    parameterSet = eqParams['parameterSet']
    # prepare report dictionary
    # Create dictionary
    reportAB = {}
    reportAB = {'headerLine': {'type': 'title', 'title': 'com2AB Simulation'},
                'avaPath': {'type': 'simName', 'name': name},
                parameterSet + 'setup': {'type': 'list',
                                         'k1': eqParams['k1'],
                                         'k2': eqParams['k2'],
                                         'k3': eqParams['k3'],
                                         'k4': eqParams['k4'],
                                         'SD': eqParams['SD']},
                'AlphaBeta results': {'type': 'list',
                                      'beta': '',
                                      'alpha': '',
                                      'alphaM1SD': '',
                                      'alphaM2SD': '',
                                      'alphaP1SD': ''},
                'AlphaBeta plots': {'type': 'image'}}

    IND = [indAlpha, indBetaPoint, indAlphaM1SD, indAlphaM2SD,
           indAlphaP1SD]
    ANGLE = [alpha, beta, alphaSD[1], alphaSD[2], alphaSD[0]]
    LABEL = ['alpha', 'beta', 'alphaM1SD', 'alphaM2SD', 'alphaP1SD']

    # write report and log
    log.info('Profile: %s with %s parameter set', name, parameterSet)
    parameterName = ['k1', 'k2', 'k3', 'k4', 'SD']
    for paramName in parameterName:
        log.info('%s = %g' % (paramName, eqParams[paramName]))
    log.info(('{:<13s}'*6).format(
        ' ', 'x [m]', 'y [m]', 'z [m]', 's [m]', 'angle [°]'))
    for ind, label, angle in zip(IND, LABEL, ANGLE):
        reportAB = addLine2Report(ind, reportAB, x, y, z, s, label, angle)

    # write results to txt file
    FileName_ext = ''
    FileName_ext = pathlib.Path(saveOutPath, name + '_AB_results.txt')
    with open(FileName_ext, 'w') as outfile:
        outfile.write('Profile name %s\n' % name)
        outfile.write('Parameter Set %s\n' % parameterSet)
        for paramName in parameterName:
            outfile.write('%s = %g\n' % (paramName, eqParams[paramName]))
        outfile.write('Alpha Beta AlMinus1SD AlMinus2SD AlPlus1SD\n')
        outfile.write(('{:<13s}'*5 + '\n').format(
            'x', 'y', 'z', 's', 'angle'))
        for ind, angle in zip(IND, ANGLE):
            writeLine(ind, outfile, x, y, z, s, angle)

    return reportAB, FileName_ext


def writeLine(ind, outfile, x, y, z, s, angle):
    if ind:
        outfile.write(('{:<13.2f}'*5 + '\n').format(
            x[ind], y[ind], z[ind], s[ind], angle))
    else:
        outfile.write(('{:<13.2f}'*5 + '\n').format(0, 0, 0, 0, 0))


def addLine2Report(ind, reportAB, x, y, z, s, label, angle):
    if ind:
        log.info(('{:<13s}'+'{:<13.2f}'*5).format(label, x[ind], y[ind],
                                                  z[ind], s[ind], angle))
        strAlpha = ('{:.2f}' + '{:s}').format(angle, '°')
    else:
        strAlpha = label + 'point out of profile'
        log.warning(strAlpha)
    reportAB['AlphaBeta results'].update({label: strAlpha})

    return reportAB
