"""
    Plotting and saving Alpha Beta results

    This file is part of Avaframe.
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
import seaborn as sns

# Local imports
from avaframe.out3Plot.plotUtils import *

# create local logger
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
        savename = name + '_AlphaBeta'
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
    rasterdata = DGM['rasterData']
    x = eqOutput['x']
    y = eqOutput['y']
    indSplit = eqOutput['indSplit']
    name = eqOutput['Name']

    if flags.getboolean('PlotPath'):
        # Plot raster and path
        fig, ax = plt.subplots(figsize=(figW, figH))
        titleText = name
        plt.title(titleText)
        cmap = copy.copy(mpl.cm.get_cmap("Greys"))
        cmap.set_bad(color='white')
        im = plt.imshow(rasterdata, cmap, origin='lower')
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)
        fig.colorbar(im, cax=cax)
        # path1 = ax1.plot((x-header.xllcorner)/header.cellsize,
        #                  (y-header.yllcorner)/header.cellsize)
        ax.plot((x-header.xllcorner)/header.cellsize,
                 (y-header.yllcorner)/header.cellsize, 'k',
                 label='avapath')
        ax.plot((splitPoint['x']-header.xllcorner)/header.cellsize,
                 (splitPoint['y']-header.yllcorner)/header.cellsize, '.',
                 color='0.3', label='Split points')
        ax.plot((x[indSplit]-header.xllcorner)/header.cellsize,
                 (y[indSplit]-header.yllcorner)/header.cellsize, '.',
                 color='0.6', label='Projection of Split Point on ava path')
        fig.legend(frameon=False, loc='lower center')
        plotUtils.putAvaNameOnPlot(ax,name)
        plt.show(block=False)


def plotProfile(DGM, eqOutput, save_file, flags):
    """ Plot and save results depending on flags options"""
    s = eqOutput['s']
    z = eqOutput['z']
    ids10Point = eqOutput['ids10Point']
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
    fig_prof = plt.figure(figsize=(1.5*figW, 1*figH))
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
    plt.axvline(x=s[ids10Point], color='0.8',
                linewidth=1, linestyle='-.', label='Beta')

    plt.plot(s, f, '-', label='AlphaLine')
    if ids_alphaM1SD:
        plt.plot(s[ids_alphaM1SD], z[ids_alphaM1SD], 'x', markersize=8,
                 label='Alpha - 1SD')
    if ids_alphaM2SD:
        plt.plot(s[ids_alphaM2SD], z[ids_alphaM2SD], 'x', markersize=8,
                 label='Alpha - 2SD')

    ax = plt.gca()
    fig_prof.tight_layout()
    versionText = datetime.datetime.now().strftime("%d.%m.%y") + \
        '; ' + 'AlphaBeta ' + ParameterSet
    plt.text(00, 0, versionText, fontsize=8, verticalalignment='bottom',
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
        log.debug('Saving profile figure to: %s', save_file)
        fig_prof.savefig(save_file)

    return save_file


def WriteResults(eqOutput, saveOutPath):
    """ Write AB results to file """
    s = eqOutput['s']
    x = eqOutput['x']
    y = eqOutput['y']
    z = eqOutput['z']
    ids10Point = eqOutput['ids10Point']
    beta = eqOutput['beta']
    alpha = eqOutput['alpha']
    alphaSD = eqOutput['alphaSD']
    ids_alpha = eqOutput['ids_alpha']
    ids_alphaP1SD = eqOutput['ids_alphaP1SD']
    ids_alphaM1SD = eqOutput['ids_alphaM1SD']
    ids_alphaM2SD = eqOutput['ids_alphaM2SD']
    parameterSet = eqOutput['ParameterSet']
    name = eqOutput['Name']

    log.info('Profile: %s with %s parameter set',  name, parameterSet)
    log.info(('{:<13s}'*6).format(
        ' ', 'x [m]', 'y [m]', 'z [m]', 's [m]', 'angle [°]'))
    if ids_alpha:
        log.info(('{:<13s}'+'{:<13.2f}'*5).format('Alpha', x[ids_alpha],
                y[ids_alpha], z[ids_alpha], s[ids_alpha], alpha))
    else:
        log.warning('alpha point out of profile')

    log.info(('{:<13s}'+'{:<13.2f}'*5).format('Beta', x[ids10Point],
                y[ids10Point], z[ids10Point], s[ids10Point], beta))
    if ids_alphaM1SD:
        log.info(('{:<13s}'+'{:<13.2f}'*5).format('alphaM1SD',
                x[ids_alphaM1SD], y[ids_alphaM1SD], z[ids_alphaM1SD],
                s[ids_alphaM1SD], alphaSD[1]))
    else:
        log.warning('alphaM1SD point out of profile')
    if ids_alphaM2SD:
        log.info(('{:<13s}'+'{:<13.2f}'*5).format('alphaM2SD',
                x[ids_alphaM2SD], y[ids_alphaM2SD], z[ids_alphaM2SD],
                s[ids_alphaM2SD], alphaSD[2]))
    else:
        log.warning('alphaM2SD point out of profile')
    if ids_alphaP1SD:
        log.info(('{:<13s}'+'{:<13.2f}'*5).format('alphaP1SD',
                x[ids_alphaP1SD], y[ids_alphaP1SD], z[ids_alphaP1SD],
                s[ids_alphaP1SD], alphaSD[0]))
    else:
        log.warning('alphaP1SD point above Beta point')

    FileName_ext = saveOutPath + name + '_AB_results.txt'
    with open(FileName_ext, 'w') as outfile:
        outfile.write('Profile name %s\n' % name)
        outfile.write('Parameter Set %s\n' % parameterSet)
        outfile.write('Alpha Beta AlMinus1SD AlMinus2SD AlPlus1SD\n')
        outfile.write(('{:<13s}'*5 + '\n').format(
            'x', 'y', 'z', 's', 'angle'))
        if ids_alpha:
            outfile.write(('{:<13.2f}'*5 + '\n').format(
                x[ids_alpha], y[ids_alpha], z[ids_alpha], s[ids_alpha], alpha))
        else:
            outfile.write(('{:<13.2f}'*5 + '\n').format(
                0,
                0,
                0,
                0,
                0))
        outfile.write(('{:<13.2f}'*5 + '\n').format(
            x[ids10Point],
            y[ids10Point],
            z[ids10Point],
            s[ids10Point],
            beta))
        if ids_alphaM1SD:
            outfile.write(('{:<13.2f}'*5 + '\n').format(
                x[ids_alphaM1SD],
                y[ids_alphaM1SD],
                z[ids_alphaM1SD],
                s[ids_alphaM1SD],
                alphaSD[1]))
        else:
            outfile.write(('{:<13.2f}'*5 + '\n').format(
                0,
                0,
                0,
                0,
                0))
        if ids_alphaM2SD:
            outfile.write(('{:<13.2f}'*5 + '\n').format(
                x[ids_alphaM2SD],
                y[ids_alphaM2SD],
                z[ids_alphaM2SD],
                s[ids_alphaM2SD],
                alphaSD[2]))
        else:
            outfile.write(('{:<13.2f}'*5 + '\n').format(
                0,
                0,
                0,
                0,
                0))
        if ids_alphaP1SD:
            outfile.write(('{:<13.2f}'*5 + '\n').format(
                x[ids_alphaP1SD],
                y[ids_alphaP1SD],
                z[ids_alphaP1SD],
                s[ids_alphaP1SD],
                alphaSD[0]))
        else:
            outfile.write(('{:<13.2f}'*5 + '\n').format(
                0,
                0,
                0,
                0,
                0))

    return FileName_ext
