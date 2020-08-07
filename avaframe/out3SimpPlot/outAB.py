#!/usr/bin/env python
# coding: utf-8
""" Main file for Post processing Alpha Beta results
"""

import pickle
import os
import logging
import copy
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.axes_grid1 import make_axes_locatable
# create local logger
# change log level in calling module to DEBUG to see log messages
log = logging.getLogger(__name__)

colors = ["#393955", "#8A8A9B", "#E9E940"]
mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=colors)


def readABresults(saveOutPath, name, flags):
    """ read the results generated by com2AB """
    savename = name + '_com2AB_eqparam.pickle'
    save_file = os.path.join(saveOutPath, savename)
    with open(save_file, 'rb') as handle:
        eqParams = pickle.load(handle)
    if not flags.getboolean('fullOut'):
        os.remove(save_file)
    savename = name + '_com2AB_eqout.pickle'
    save_file = os.path.join(saveOutPath, savename)
    with open(save_file, 'rb') as handle:
        eqOut = pickle.load(handle)
    if not flags.getboolean('fullOut'):
        os.remove(save_file)

    return eqParams, eqOut


def processABresults(eqParams, eqOut):
    """ prepare AlphaBeta results for plotting and writing results """

    s = eqOut['s']
    z = eqOut['z']
    CuSplit = eqOut['CuSplit']
    alpha = eqOut['alpha']
    alphaSD = eqOut['alphaSD']

    # Line down to alpha
    f = z[0] + np.tan(np.deg2rad(-alpha)) * s
    fplus1SD = z[0] + np.tan(np.deg2rad(-alphaSD[0])) * s
    fminus1SD = z[0] + np.tan(np.deg2rad(-alphaSD[1])) * s
    fminus2SD = z[0] + np.tan(np.deg2rad(-alphaSD[2])) * s

    # First it calculates f - g and the corresponding signs
    # using np.sign. Applying np.diff reveals all
    # the positions, where the sign changes (e.g. the lines cross).
    ids_alpha = np.argwhere(np.diff(np.sign(f - z))).flatten()
    ids_alphaP1SD = np.argwhere(np.diff(np.sign(fplus1SD - z))).flatten()
    ids_alphaM1SD = np.argwhere(np.diff(np.sign(fminus1SD - z))).flatten()
    ids_alphaM2SD = np.argwhere(np.diff(np.sign(fminus2SD - z))).flatten()

    # Only get the first index past the splitpoint
    try:
        ids_alpha = ids_alpha[s[ids_alpha] > CuSplit][0]
    except IndexError:
        log.warning('Alpha out of profile')
        ids_alpha = None

    try:
        ids_alphaP1SD = ids_alphaP1SD[s[ids_alphaP1SD] > CuSplit][0]
    except IndexError:
        log.warning('+1 SD above beta point')
        ids_alphaP1SD = None

    try:
        ids_alphaM1SD = ids_alphaM1SD[s[ids_alphaM1SD] > CuSplit][0]
    except IndexError:
        log.warning('-1 SD out of profile')
        ids_alphaM1SD = None

    try:
        ids_alphaM2SD = ids_alphaM2SD[s[ids_alphaM2SD] > CuSplit][0]
    except IndexError:
        log.warning('-2 SD out of profile')
        ids_alphaM2SD = None

    eqOut['f'] = f
    eqOut['ids_alpha'] = ids_alpha
    eqOut['ids_alphaP1SD'] = ids_alphaP1SD
    eqOut['ids_alphaM1SD'] = ids_alphaM1SD
    eqOut['ids_alphaM2SD'] = ids_alphaM2SD

    ParameterSet = eqParams['ParameterSet']
    eqOut['ParameterSet'] = ParameterSet

    return eqOut


def writeABpostOut(DGM, Avapath, SplitPoint, saveOutPath, flags):
    """ Loops on the given Avapath, runs AlpahBeta Postprocessing
    plots Results and Write Results
    """
    NameAva = Avapath['Name']
    FileNamePlot_ext = [None] * len(NameAva)
    FileNameWrite_ext = [None] * len(NameAva)
    for i in range(len(NameAva)):
        name = NameAva[i]
        eqParams, eqOut = readABresults(saveOutPath, name, flags)
        eqPost = processABresults(eqParams, eqOut)
        # Plot the whole profile with beta, alpha ... points and lines
        savename = name + '_AlphaBeta.pdf'
        save_file = os.path.join(saveOutPath, savename)
        plotPath(DGM, SplitPoint, eqPost, flags)
        FileNamePlot_ext[i] = plotProfile(DGM, eqPost, save_file, flags)
        if flags.getboolean('WriteRes'):
            FileNameWrite_ext[i] = WriteResults(eqPost, saveOutPath)
    if flags.getboolean('PlotPath') or flags.getboolean('PlotProfile'):
        plt.pause(0.001)
        input("Press [enter] to continue.")
    return FileNamePlot_ext, FileNameWrite_ext


def plotPath(DGM, splitPoint, eqOutput, flags):
    """ Plot and save results depending on flags options"""
    header = DGM['header']
    rasterdata = DGM['rasterdata']
    x = eqOutput['x']
    y = eqOutput['y']
    indSplit = eqOutput['indSplit']
    name = eqOutput['Name']

    if flags.getboolean('PlotPath'):
        # Plot raster and path
        fig1, ax1 = plt.subplots()
        titleText = name
        plt.title(titleText)
        cmap = copy.copy(mpl.cm.get_cmap("Greys"))
        cmap.set_bad(color='white')
        im1 = plt.imshow(rasterdata, cmap, origin='lower')
        divider = make_axes_locatable(ax1)
        cax = divider.append_axes("right", size="5%", pad=0.1)
        fig1.colorbar(im1, cax=cax)
        # path1 = ax1.plot((x-header.xllcorner)/header.cellsize,
        #                  (y-header.yllcorner)/header.cellsize)
        ax1.plot((x-header.xllcorner)/header.cellsize,
                 (y-header.yllcorner)/header.cellsize, 'k',
                 label='avapath')
        ax1.plot((splitPoint['x']-header.xllcorner)/header.cellsize,
                 (splitPoint['y']-header.yllcorner)/header.cellsize, '.',
                 color='0.3', label='Split points')
        ax1.plot((x[indSplit]-header.xllcorner)/header.cellsize,
                 (y[indSplit]-header.yllcorner)/header.cellsize, '.',
                 color='0.6', label='Projection of Split Point on ava path')
        fig1.legend(frameon=False, loc='lower center')
        plt.show(block=False)


def plotProfile(DGM, eqOutput, save_file, flags):
    """ Plot and save results depending on flags options"""
    s = eqOutput['s']
    z = eqOutput['z']
    ids_10Point = eqOutput['ids_10Point']
    poly = eqOutput['poly']
    beta = eqOutput['beta']
    alpha = eqOutput['alpha']
    f = eqOutput['f']
    ids_alphaM1SD = eqOutput['ids_alphaM1SD']
    ids_alphaM2SD = eqOutput['ids_alphaM2SD']
    indSplit = eqOutput['indSplit']
    ParameterSet = eqOutput['ParameterSet']
    name = eqOutput['Name']
    # Plot the whole profile with beta, alpha ... points and lines
    # plt.close("all")
    fig_prof = plt.figure(figsize=(10, 6))
    titleText = name
    plt.title(titleText)

    xlabelText = 'Distance [m]\nBeta: ' + str(round(beta, 1)) + \
        '$^\circ$' + '  Alpha: ' + str(round(alpha, 1)) + '$^\circ$'
    plt.xlabel(xlabelText, multialignment='center')

    plt.ylabel('Height [m]')

    plt.plot(s, z, '-', label='DEM')
    plt.plot(s, poly(s), ':', label='QuadFit')
    plt.axvline(x=s[indSplit], color='0.7',
                linewidth=1, linestyle='--', label='Split point')
    plt.axvline(x=s[ids_10Point], color='0.8',
                linewidth=1, linestyle='-.', label='Beta')

    plt.plot(s, f, '-', label='AlphaLine')
    if ids_alphaM1SD:
        plt.plot(s[ids_alphaM1SD], z[ids_alphaM1SD], 'x', markersize=8,
                 label='Alpha - 1SD')
    if ids_alphaM2SD:
        plt.plot(s[ids_alphaM2SD], z[ids_alphaM2SD], 'x', markersize=8,
                 label='Alpha - 2SD')

    ax = plt.gca()

    versionText = datetime.datetime.now().strftime("%d.%m.%y") + \
        '; ' + 'AlphaBeta ' + ParameterSet
    plt.text(0, 0, versionText, fontsize=8, verticalalignment='bottom',
             horizontalalignment='left', transform=ax.transAxes,
             color='0.5')
    # plt.text(-0.2, 0, 'matplotlib -2', \
    #          verticalalignment='center', transform=ax.transAxes)

    plt.gca().set_aspect('equal', adjustable='box')
    plt.grid(linestyle=':', color='0.9')
    plt.legend(frameon=False)
    plt.draw()
    if flags.getboolean('PlotProfile'):
        plt.show(block=False)
    if flags.getboolean('SaveProfile'):
        log.info('Saving profile figure to: %s', save_file)
        fig_prof.savefig(save_file)
    # plt.close(fig_prof)
    # plt.close("all")
    return save_file


def WriteResults(eqOutput, saveOutPath):
    """ Write AB results to file """
    s = eqOutput['s']
    x = eqOutput['x']
    y = eqOutput['y']
    z = eqOutput['z']
    ids_10Point = eqOutput['ids_10Point']
    beta = eqOutput['beta']
    alpha = eqOutput['alpha']
    alphaSD = eqOutput['alphaSD']
    ids_alpha = eqOutput['ids_alpha']
    ids_alphaP1SD = eqOutput['ids_alphaP1SD']
    ids_alphaM1SD = eqOutput['ids_alphaM1SD']
    ids_alphaM2SD = eqOutput['ids_alphaM2SD']
    ParameterSet = eqOutput['ParameterSet']
    name = eqOutput['Name']

    log.info('Profile name %s' % name)
    log.info('Parameter Set %s' % ParameterSet)
    log.info('Alpha point (x,y,z,s) in [m]:(%.2f,%.2f,%.2f,%.2f) and'
             ' angle in [°] : %.2f' % (x[ids_alpha], y[ids_alpha],
                                       z[ids_alpha], s[ids_alpha], alpha))
    log.info('Beta point (x,y,z,s) in [m]:(%.2f,%.2f,%.2f,%.2f) and'
             ' angle in [°] : %.2f' % (x[ids_10Point], y[ids_10Point],
                                       z[ids_10Point], s[ids_10Point], beta))
    if ids_alphaM1SD:
        log.info('alphaM1SD point (x,y,z,s) in [m]:(%.2f,%.2f,%.2f,%.2f) and'
                 ' angle in [°] : %.2f' % (x[ids_alphaM1SD], y[ids_alphaM1SD],
                                           z[ids_alphaM1SD], s[ids_alphaM1SD],
                                           alphaSD[1]))
    else:
        log.warning('alphaM1SD point out of profile')
    if ids_alphaM2SD:
        log.info('alphaM2SD point (x,y,z,s) in [m]:(%.2f,%.2f,%.2f,%.2f) and'
                 ' angle in [°] : %.2f' % (x[ids_alphaM2SD], y[ids_alphaM2SD],
                                           z[ids_alphaM2SD], s[ids_alphaM2SD],
                                           alphaSD[2]))
    else:
        log.warning('alphaM2SD point out of profile')
    log.info('alphaP1SD point (x,y,z,s) in [m]:(%.2f,%.2f,%.2f,%.2f) and'
             ' angle  in [°] : %.2f' % (x[ids_alphaP1SD], y[ids_alphaP1SD],
                                        z[ids_alphaP1SD], s[ids_alphaP1SD],
                                        alphaSD[0]))

    FileName_ext = saveOutPath + name + '_results_python.txt'
    with open(FileName_ext, 'w') as outfile:
        outfile.write('Profile name %s\n' % name)
        outfile.write('Parameter Set %s\n' % ParameterSet)
        outfile.write('x y z s angle\n')
        outfile.write('Alpha Beta AlMinus1SD AlMinus2SD AlPlus1SD\n')
        outfile.write('%.2f %.2f %.2f %.2f %.2f\n' % (
            x[ids_alpha], y[ids_alpha], z[ids_alpha], s[ids_alpha], alpha))
        outfile.write('%.2f %.2f %.2f %.2f %.2f\n' % (x[ids_10Point],
                                                      y[ids_10Point],
                                                      z[ids_10Point],
                                                      s[ids_10Point],
                                                      beta))
        if ids_alphaM1SD:
            outfile.write('%.2f %.2f %.2f %.2f %.2f\n' % (x[ids_alphaM1SD],
                                                          y[ids_alphaM1SD],
                                                          z[ids_alphaM1SD],
                                                          s[ids_alphaM1SD],
                                                          alphaSD[1]))
        else:
            outfile.write('alphaM1SD point out of profile\n')
        if ids_alphaM2SD:
            outfile.write('%.2f %.2f %.2f %.2f %.2f\n' % (x[ids_alphaM2SD],
                                                          y[ids_alphaM2SD],
                                                          z[ids_alphaM2SD],
                                                          s[ids_alphaM2SD],
                                                          alphaSD[2]))
        else:
            outfile.write('alphaM2SD point out of profile\n')
        outfile.write('%.2f %.2f %.2f %.2f %.2f\n' % (x[ids_alphaP1SD],
                                                      y[ids_alphaP1SD],
                                                      z[ids_alphaP1SD],
                                                      s[ids_alphaP1SD],
                                                      alphaSD[0]))
    return FileName_ext
