"""
    Plotting and saving AIMEC results

    This file is part of Avaframe.
"""

import os
import logging
import math
import numpy as np
from matplotlib import pyplot as plt
import matplotlib
from matplotlib import cm


# Local imports
import avaframe.out3Plot.plotUtils as pU
import avaframe.out3Plot.makePalette as makePalette

# create local logger
log = logging.getLogger(__name__)


def visuTransfo(rasterTransfo, inputData, cfgPath, cfgFlags):
    """
    Plot and save the domain transformation figure
    """
    ####################################
    # Get input data
    # read paths
    projectName = cfgPath['projectName']
    #dirName = cfgPath['dirName']
    # read rasterdata
    slRaster = inputData['slRaster']
    xyRaster = inputData['xyRaster']
    # read avaPath with scale
    xPath = rasterTransfo['x']
    yPath = rasterTransfo['y']
    # read domain boundarries with scale
    xllc = rasterTransfo['xllc']
    yllc = rasterTransfo['yllc']
    cellsize = rasterTransfo['cellsize']
    DBXl = rasterTransfo['DBXl']*cellsize+xllc
    DBXr = rasterTransfo['DBXr']*cellsize+xllc
    DBYl = rasterTransfo['DBYl']*cellsize+yllc
    DBYr = rasterTransfo['DBYr']*cellsize+yllc

    ############################################
    # prepare for plot
    n, m = np.shape(xyRaster)
    x = np.arange(m)*cellsize+xllc
    y = np.arange(n)*cellsize+yllc
    indStartOfRunout = rasterTransfo['indStartOfRunout']
    xx = rasterTransfo['x'][indStartOfRunout]
    yy = rasterTransfo['y'][indStartOfRunout]

    l = rasterTransfo['l']
    s = rasterTransfo['s']

    maskedArray = np.ma.masked_where(xyRaster == 0, xyRaster)
    maskedArraySL = np.ma.masked_where(slRaster == 0, slRaster)

    cmap, _, _, norm, ticks = makePalette.makeColorMap(
        pU.cmapPres, 0.0, np.nanmax(maskedArray), continuous=pU.contCmap)
    cmap.set_under(color='w')

    ############################################
    # Figure: Raster transformation
    fig = plt.figure(figsize=(pU.figW*2, pU.figH))

    ax1 = plt.subplot(121)

    ref0, im = pU.NonUnifIm(ax1, x, y, maskedArray, 'x [m]', 'y [m]',
                         extent=[x.min(), x.max(), y.min(), y.max()],
                         cmap=cmap, norm=norm)
    plt.plot(xx, yy, 'k+', label='start of run-out area point : %.1f °' %
             rasterTransfo['startOfRunoutAngle'])
    plt.plot(xPath, yPath, 'k--', label='flow path')
    plt.plot(DBXl, DBYl, 'k-', label='domain')
    plt.plot(DBXr, DBYr, 'k-')
    plt.plot([DBXl, DBXr], [DBYl, DBYr], 'k-')

    ax1.set_title('XY Domain')
    ax1.legend(loc=4)
    pU.putAvaNameOnPlot(ax1, cfgPath['projectName'])

    ax2 = plt.subplot(122)

    ref0, im = pU.NonUnifIm(ax2, l, s, maskedArraySL, 'l [m]', 's [m]',
                         extent=[l.min(), l.max(), s.min(), s.max()],
                         cmap=cmap, norm=norm)
    ax2.axhline(y=s[indStartOfRunout], color='k', linestyle='--',
                label='start of run-out area point : %.1f °' % rasterTransfo['startOfRunoutAngle'])

    ax2.set_title('sl Domain' + '\n' + 'Black = out of raster')
    ax2.legend(loc=4)
    pU.addColorBar(im, ax2, ticks, pU.cfgPlotUtils['unitppr'])

    #outFileName = '_'.join([projectName, dirName, 'DomainTransformation'])
    outFileName = '_'.join([projectName, 'DomainTransformation'])
    pU.saveAndOrPlot(cfgPath, cfgFlags, outFileName, fig)


def visuRunoutComp(rasterTransfo, resAnalysis, plim, newRasters, cfgPath, cfgFlags):
    """
    Plot and save the Peak Pressure  distribution after coord transfo
    """
    ####################################
    # Get input data
    # read paths
    projectName = cfgPath['projectName']
    #dirName = cfgPath['dirName']
    # read data
    s = rasterTransfo['s']
    l = rasterTransfo['l']
    PPRCrossMax = resAnalysis['PPRCrossMax']
    PPRCrossMean = resAnalysis['PPRCrossMean']
    PFDCrossMax = resAnalysis['PFDCrossMax']
    PFDCrossMean = resAnalysis['PFDCrossMean']
    PFVCrossMax = resAnalysis['PFVCrossMax']
    PFVCrossMean = resAnalysis['PFVCrossMean']

    ############################################
    # prepare for plot
    Title = ['Pressure ', 'Flow Depth ', 'Flow Velocity ']
    Unit = ['$P(s)$ [kPa]', '$fd(s)$ [m]', '$v(s) [m.s^{-1}]$']
    DataMax = np.array(([None] * 3))
    DataMax[0] = PPRCrossMax
    DataMax[1] = PFDCrossMax
    DataMax[2] = PFVCrossMax

    DataMean = np.array(([None] * 3))
    DataMean[0] = PPRCrossMean
    DataMean[1] = PFDCrossMean
    DataMean[2] = PFVCrossMean

    ############################################
    # Figure: Pressure depth speed

    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(pU.figW*3, pU.figH))
    fig.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95, hspace=0.3)

    for ax, dataMax, dataMean, title, unit in zip(axes.flatten(), DataMax, DataMean, Title, Unit):
        ax.plot(dataMax[0, :], s, '--k', label='Max Reference')
        ax.plot(dataMean[0, :], s, '-k', label='Mean Reference')
        ax.plot(dataMax[1, :], s, '--b', label='Max Simulation')
        ax.plot(dataMean[1, :], s, '-b', label='Mean Simulation')

        ax.set_title(title + 'distribution along the path')
        ax.legend(loc=4)
        ax.set_ylabel('s [m]')
        ax.set_ylim([s.min(), s.max()])
        ax.set_xlim(auto=True)
        ax.set_xlabel(unit)
    pU.putAvaNameOnPlot(ax, cfgPath['projectName'])
    #outFileName = '_'.join([projectName, dirName, 'plim',
    #                        str(int(plim)), 'slComparison'])
    outFileName = '_'.join([projectName, 'plim',
                            str(int(plim)), 'slComparison'])
    pU.saveAndOrPlot(cfgPath, cfgFlags, outFileName, fig)


def visuRunoutStat(rasterTransfo, resAnalysis, plim, newRasters, cfgPath, cfgFlags):
    """
    Plot and save the Peak Pressure  distribution after coord transfo
    """
    ####################################
    # Get input data
    # read paths
    projectName = cfgPath['projectName']
    #dirName = cfgPath['dirName']
    nRef = cfgPath['referenceFile']
    # read data
    s = rasterTransfo['s']
    l = rasterTransfo['l']
    indStartOfRunout = rasterTransfo['indStartOfRunout']
    dataPressure = newRasters['newRasterPressure']
    rasterdataPres = dataPressure[nRef]
    runout = resAnalysis['runout'][0]
    PPRCrossMax = resAnalysis['PPRCrossMax']

    ############################################
    # prepare for plot
    pMean = np.mean(PPRCrossMax, axis=0)
    pMedian = np.median(PPRCrossMax, axis=0)
    pPercentile = np.percentile(PPRCrossMax, [2.5, 50, 97.5], axis=0)

    maskedArray = np.ma.masked_where(rasterdataPres == 0, rasterdataPres)

    cmap, _, _, norm, ticks = makePalette.makeColorMap(pU.cmapPres, 0.0,
                                                       np.nanmax(maskedArray),
                                                       continuous=pU.contCmap)
    cmap.set_bad('w', 1.)

    ############################################
    # Figure: Analysis runout
    fig = plt.figure(figsize=(pU.figW*2, pU.figH))
    ax1 = plt.subplot(121)

    ax1.axhline(y=np.max(runout), color='k', linestyle='-.', label='runout max')
    ax1.axhline(y=np.average(runout), color='k', linestyle='-', label='runout mean')
    ax1.axhline(y=np.min(runout), color='k', linestyle=':', label='runout min')

    ax1.axhline(y=s[indStartOfRunout], color='k', linestyle='--',
                label='start of run-out area point : %.1f °' % resAnalysis['startOfRunoutAngle'])
    ref5, im = pU.NonUnifIm(ax1, l, s, maskedArray, 'l [m]', 's [m]',
                         extent=[l.min(), l.max(), s.min(), s.max()],
                         cmap=cmap, norm=norm)

    ax1.set_title('Peak Pressure 2D plot for the reference')
    ax1.legend(loc=4)
    pU.putAvaNameOnPlot(ax1, cfgPath['projectName'])
    pU.addColorBar(im, ax1, ticks, pU.cfgPlotUtils['unitppr'])

    ax2 = plt.subplot(122)

    ax2.fill_betweenx(s, pPercentile[2], pPercentile[0],
                      facecolor=[.8, .8, .8], alpha=0.5, label='quantiles')
    matplotlib.patches.Patch(alpha=0.5, color=[.8, .8, .8])
    ax2.plot(pMedian, s, color='r', label='median')
    ax2.plot(pMean, s, color='b', label='mean')

    ax2.set_title('Peak Pressure distribution along the path between runs')
    ax2.legend(loc=4)
    ax2.set_ylabel('s [m]')
    ax2.set_ylim([s.min(), s.max()])
    ax2.set_xlim(auto=True)
    ax2.set_xlabel('$P_{max}(s)$ [kPa]')

    #outFileName = '_'.join([projectName, dirName, 'plim',
    #                        str(int(plim)), 'slComparisonStat'])
    outFileName = '_'.join([projectName, 'plim',  str(int(plim)), 'slComparisonStat'])


    pU.saveAndOrPlot(cfgPath, cfgFlags, outFileName, fig)


def visuMass(resAnalysis, cfgPath, cfgFlags):
    """
    Plot and save the comparison between current simulation and Reference
    in the run-out area
    """
    ####################################
    # Get input data
    # read paths
    projectName = cfgPath['projectName']
    #dirName = cfgPath['dirName']
    # read data
    entMassArray = resAnalysis['entMassArray']
    totalMassArray = resAnalysis['totalMassArray']
    time = resAnalysis['time']

    ############################################
    # prepare for plot
    Title = ['Entrained ', 'Total ']
    Unit = ['Entrained Mass ', 'Total Mass ']
    DataMass = np.array(([None] * 2))
    DataMass[0] = entMassArray
    DataMass[1] = totalMassArray

    ############################################
    # Figure: Pressure depth speed

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(pU.figW*2, pU.figH))
    fig.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95, hspace=0.3)

    for ax, dataMass, title, unit in zip(axes.flatten(), DataMass, Title, Unit):
        ax.plot(time, dataMass[0, :], '-k', label='Reference')
        ax.plot(time, dataMass[1, :], '-b', label='Simulation')

        ax.set_title(title + 'mass function of time')
        ax.legend(loc=4)
        ax.set_xlabel('t [s]')
        ax.set_ylabel(unit + '[kg]')

    #outFileName = '_'.join([projectName, dirName, 'massAnalysis'])
    outFileName = '_'.join([projectName, 'massAnalysis'])


    pU.saveAndOrPlot(cfgPath, cfgFlags, outFileName, fig)


def visuSimple(rasterTransfo, resAnalysis, newRasters, cfgPath, cfgFlags):
    """
    Plot and save the Peak Pressure Peak Flow depth and Peak speed
    fields after coord transfo
    """
    ####################################
    # Get input data
    # read paths
    projectName = cfgPath['projectName']
    #dirName = cfgPath['dirName']
    nRef = cfgPath['referenceFile']
    # read data
    plim = resAnalysis['pressureLimit']
    s = rasterTransfo['s']
    l = rasterTransfo['l']
    indStartOfRunout = rasterTransfo['indStartOfRunout']
    dataPressure = newRasters['newRasterPressure']
    rasterdataPres = dataPressure[nRef]
    dataDepth = newRasters['newRasterDepth']
    rasterdataDepth = dataDepth[nRef]
    dataSpeed = newRasters['newRasterSpeed']
    rasterdataSpeed = dataSpeed[nRef]
    runout = resAnalysis['runout'][0]

    ############################################
    # prepare for plot
    Cmap = [pU.cmapPres, pU.cmapDepth, pU.cmapSpeed]
    Title = ['Peak Pressure', 'Peak Flow Depth', 'Peak Speed']
    Unit = [pU.cfgPlotUtils['unitppr'], pU.cfgPlotUtils['unitpfd'], pU.cfgPlotUtils['unitpfv']]
    Data = np.array(([None] * 3))
    Data[0] = rasterdataPres
    Data[1] = rasterdataDepth
    Data[2] = rasterdataSpeed

    ############################################
    # Figure: Pressure depth speed

    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(pU.figW*3, pU.figH))
    fig.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95, hspace=0.3)

    for ax, cmap, data, title, unit in zip(axes.flatten(), Cmap, Data, Title, Unit):
        maskedArray = np.ma.masked_where(data == 0, data)
        cmap, _, _, norm, ticks = makePalette.makeColorMap(
            cmap, 0.0, np.nanmax(maskedArray), continuous=pU.contCmap)
        cmap.set_bad('w', 1.)
        ax.axhline(y=runout[0], color='k', linestyle='-', label='runout')

        ax.axhline(y=s[indStartOfRunout], color='k', linestyle='--',
                   label='Start or run-out point : %.1f °' % resAnalysis['startOfRunoutAngle'])
        ref3, im = pU.NonUnifIm(ax, l, s, maskedArray, 'l [m]', 's [m]',
                             extent=[l.min(), l.max(), s.min(), s.max()],
                             cmap=cmap, norm=norm)

        ax.set_title(title)
        ax.legend(loc=4)
        pU.addColorBar(im, ax, ticks, unit)
        pU.putAvaNameOnPlot(ax, cfgPath['projectName'])

    # outFileName = '_'.join([projectName, dirName,'plim',
    #                         str(int(plim)), 'referenceFields'])
    outFileName = '_'.join([projectName, 'plim',
                            str(int(plim)), 'referenceFields'])

    pU.saveAndOrPlot(cfgPath, cfgFlags, outFileName, fig)


def visuComparison(rasterTransfo, inputs, cfgPath, cfgFlags):
    """
    Plot and save the comparison between current simulation and Reference
    in the run-out area
    """
    ####################################
    # Get input data
    # read paths
    projectName = cfgPath['projectName']
    #dirName = cfgPath['dirName']
    # read data
    s = rasterTransfo['s']
    l = rasterTransfo['l']
    indStartOfRunout = rasterTransfo['indStartOfRunout']
    sStart = s[indStartOfRunout]
    pLim = inputs['pressureLimit']
    runoutLength = inputs['runoutLength']
    refDataPressure = inputs['refDataPressure']
    refRasterMask = inputs['refRasterMask']
    newRasterMask = inputs['newRasterMask']
    nStart = inputs['nStart']
    i = inputs['i']

    ############################################
    # Figure: Raster comparison
    fig = plt.figure(figsize=(pU.figW*2, pU.figH))
    ax1 = plt.subplot(121)

    # get color map
    cmap, _, _, norm, ticks = makePalette.makeColorMap(pU.cmapPres, pLim,
                                                       np.nanmax((refDataPressure)[nStart:]),
                                                       continuous=pU.contCmap)
    cmap.set_under(color='w')

    ref0, im = pU.NonUnifIm(ax1, l, s, refDataPressure, 'l [m]', 's [m]',
                         extent=[l.min(), l.max(), s.min(), s.max()],
                         cmap=cmap, norm=norm)
    im.set_clim(vmin=pLim, vmax=np.nanmax((refDataPressure)[nStart:]))

    ax1.set_title('Reference Peak Pressure in the RunOut area' +
                  '\n' + 'Pressure threshold: %.1f kPa' % pLim)
    pU.addColorBar(im, ax1, ticks, pU.cfgPlotUtils['unitppr'])

    y_lim = s[indStartOfRunout+20]+np.nanmax(runoutLength-sStart)
    ax1.set_ylim([s[indStartOfRunout], y_lim])
    pU.putAvaNameOnPlot(ax1, projectName)
    ax2 = plt.subplot(122)
    colorsList = [[0, 0, 1], [1, 1, 1], [1, 0, 0]]
    cmap = matplotlib.colors.ListedColormap(colorsList)
    cmap.set_under(color='b')
    cmap.set_over(color='r')
    cmap.set_bad(color='k')
    ref0, im = pU.NonUnifIm(ax2, l, s, newRasterMask-refRasterMask, 'l [m]', 's [m]',
                         extent=[l.min(), l.max(), s.min(), s.max()], cmap=cmap)

    ax2.set_title(
        'Difference between current and reference in the RunOut area' + '\n' + 'Blue = FN, Red = FP')
    im.set_clim(vmin=-0.000000001, vmax=0.000000001)
    ax2.set_ylim([s[indStartOfRunout], y_lim])
    plt.subplots_adjust(wspace=0.3)

    #outFileName = '_'.join([projectName, dirName, 'plim', str(int(pLim)),  str(i), 'comparisonToReference'])
    outFileName = '_'.join([projectName, 'plim', str(int(pLim)),  str(i), 'comparisonToReference'])


    pU.saveAndOrPlot(cfgPath, cfgFlags, outFileName, fig)


def resultWrite(cfgPath, cfgSetup, rasterTransfo, resAnalysis):
    """
    This function writes the main Aimec results to a file (outputFile)
    in cfgPath
    """
    ####################################
    # Get input data
    projectName = cfgPath['projectName']
    #dirName = cfgPath['dirName']
    pathResult = cfgPath['pathResult']
    pathName = cfgPath['pathName']
    demName = os.path.basename(cfgPath['demSource'])
    dataName = [os.path.basename(name) for name in cfgPath['ppr']]
    domainWidth = cfgSetup['domainWidth']
    pressureLimit = cfgSetup['pressureLimit']

    startOfRunoutAngle = resAnalysis['startOfRunoutAngle']
    indStartOfRunout = rasterTransfo['indStartOfRunout']
    s = rasterTransfo['s']
    sStart = s[indStartOfRunout]
    runoutFromMid = resAnalysis['runout'][0] - sStart
    runout = resAnalysis['runout']
    MMPPR = resAnalysis['MMPPR']
    MMPFD = resAnalysis['MMPFD']
    MMPFV = resAnalysis['MMPFV']
    deltaH = resAnalysis['deltaH']
    elevRel = resAnalysis['elevRel']
    relMass = resAnalysis['relMass']
    entMass = resAnalysis['entMass']
    relativMassDiff = resAnalysis['relativMassDiff']
    finalMass = resAnalysis['finalMass']
    GI = resAnalysis['growthIndex']
    GR = resAnalysis['growthGrad']
    TP = resAnalysis['TP']
    FN = resAnalysis['FN']
    FP = resAnalysis['FP']
    TN = resAnalysis['TN']
    areaSum = TP + FN

    ############################################
    # prepare for writing
    legend = ['fileNr', 'Xrunout', 'Yrunout', 'Lrunout', 'runoutFromSROA', 'elevRel', 'deltaH',
              'MMPPR', 'MMPFD', 'MMPFV', 'relMass', 'entMass',
              'finalMass', 'rMassDif', 'GI', 'GR', 'TP ', 'FN ', 'FP ', 'TN']
    resfile = [runout[1], runout[2], runout[0], runoutFromMid, elevRel, deltaH, MMPPR,
               MMPFD, MMPFV, relMass, entMass, finalMass, relativMassDiff,
               GI, GR, TP/areaSum, FN/areaSum, FP/areaSum, TN/areaSum]

    header = ''.join(['projectName: ', projectName, '\n',
                      'path: ', pathName, '\n',
                      'dhm: ', demName, '\n',
                      'domain_width: ', str(domainWidth), ' m\n',
                      'pressure_limit: ', str(pressureLimit), ' kPa\n',
                      'start of runout area Angle (SROA angle): ', str(round(startOfRunoutAngle, 2)), ' °\n'])

    # outFileName = '_'.join(['Results', projectName, '', dirName, '', 'plim',
    #                         str(pressureLimit), 'w', str(domainWidth)]) + '.txt'
    outFileName = '_'.join(['Results', projectName, '', '', 'plim',
                            str(pressureLimit), 'w', str(domainWidth)]) + '.txt'
    outname = os.path.join(pathResult, outFileName)

    # check if folder exists / create
    if not os.path.exists(os.path.dirname(outname)):
        os.makedirs(os.path.dirname(outname))

    ############################################
    # write results to file
    output = resfile
    log.info('write output file: %s' % outname)
    fid = open(outname, 'w')
    fid.write(header)
    # write table legend
    for j in range(len(legend)):
        fid.write('{:<15s}'.format(legend[j]))
    fid.write('\n')
    # write table values
    for i in range(np.shape(output)[1]):
        fid.write('{:<15d}'.format(i))
        for j in range(np.shape(output)[0]):
            try:
                fid.write('{:<15.3f}'.format(output[j][i]))
            except:
                fid.write('{:<15}'.format('NaN'))
        fid.write('\n')
    for i in range(np.shape(output)[1]):
        tmp = os.path.basename(dataName[i])
        name = os.path.splitext(tmp)[0]
        fid.write('file number: %d = %s \n' %(i, name))
    fid.close()

    log.info('File written: %s' % outname)


def resultVisu(cfgPath, cfgFlags, rasterTransfo, resAnalysis, plim):
    """
    Visualize results in a nice way
    """
    ####################################
    # Get input data
    fnames = cfgPath['ppr']
    nRef = cfgPath['referenceFile']

    flag = float(cfgFlags['typeFlag'])

    zPath = rasterTransfo['z']
    sPath = rasterTransfo['s']

    indStartOfRunout = rasterTransfo['indStartOfRunout']
    sStart = sPath[indStartOfRunout]
    runout = resAnalysis['runout'][0]
    maxMaxDPPR = resAnalysis['MMPPR']
    GI = resAnalysis['growthIndex']

    # prepare for plot
    if flag == 2:
        title = 'Visualizing EGU growth index data'
        tipo = 'growthInd'
        data = GI
        yaxis_label = 'growth index [GI]'

    elif flag == 3:
        title = 'Visualizing max peak pressure data'
        tipo = 'relMaxPeakPres'
        data = maxMaxDPPR / maxMaxDPPR[nRef]
        yaxis_label = 'relative max peak pressure [-]'

    else:
        log.error('Wrong flag')
        return None

    log.info(title)

    # If more than 100 files are provided, add a density plot
    plotDensity = 0
    if (len(fnames) > 100):
        plotDensity = 1

    color = pU.cmapAimec(np.linspace(1, 0, len(runout) + 3, dtype=float))
    mk = 0

    #######################################
    # Final result diagram - z_profile+data

    fig = plt.figure(figsize=(pU.figW*2, pU.figH))

    # show flow path
    ax1 = fig.add_subplot(111)
    ax1.set_title(title)
    ax1.set_ylabel(yaxis_label, color=color[-3])
    ax1.spines['left'].set_color(color[-3])
    ax1.tick_params(axis='y', colors=color[-3])
    ax1.set_xlabel(''.join(['s [m] - runout with ', str(plim),
                            ' kPa threshold']))
    pU.putAvaNameOnPlot(ax1, cfgPath['projectName'])
    if plotDensity:  # estimate 2D histogram --> create pcolormesh
        nbins = 100
        H, xedges, yedges = np.histogram2d(runout, data, bins=nbins)
        H = np.flipud(np.rot90(H))
        Hmasked = np.ma.masked_where(H == 0, H)
        dataDensity = plt.pcolormesh(xedges, yedges, Hmasked, cmap=cm.Blues)
        cbar = plt.colorbar(dataDensity, orientation='horizontal')
        cbar.ax.set_ylabel('Counts')

    ax2 = ax1.twinx()
    ax2.set_ylabel('z [m]')
    ax2.spines['left'].set_color(color[-3])
    ax2.tick_params(axis='y', colors='k')
    ax2.plot(sPath, zPath, color='k', label='path', linestyle='--')
    plt.xlim([0, max(sPath) + 50])
    plt.ylim([math.floor(min(zPath)/10)*10, math.ceil(max(zPath)/10)*10])

    if not plotDensity:
        for k in range(len(runout)):
            topoName = cfgPath['projectName']
            pfarbe = color[k+1]
            if k == 0:
                ax1.plot(runout[k], data[k], marker='+', linestyle='None',
                         markersize=2*pU.ms, color='g', label='Reference')
            elif k == 1:
                ax1.plot(runout[k], data[k], marker=pU.markers, label='sims',
                         color=pfarbe, linestyle='None')
            else:
                ax1.plot(runout[k], data[k], marker=pU.markers, color=pfarbe,
                         linestyle='None')
            mk = mk+1
            if mk == len(pU.markers):
                mk = 1
        ax1.legend(loc=4)

    ax1.grid('on')

    #utFileName = '_'.join([cfgPath['projectName'], cfgPath['dirName'],
    #                    'plim', str(int(plim)), tipo])
    outFileName = '_'.join([cfgPath['projectName'],
                        'plim', str(int(plim)), tipo])

    pU.saveAndOrPlot(cfgPath, cfgFlags, outFileName, fig)

    ############################################
    # Final result diagram - roc-plots

    rTP = resAnalysis['TP'] / (resAnalysis['TP'][nRef] + resAnalysis['FN'][nRef])
    rFP = resAnalysis['FP'] / (resAnalysis['TP'][nRef] + resAnalysis['FN'][nRef])

    fig = plt.figure(figsize=(pU.figW, pU.figH))
    mk = 0
    ax1 = fig.add_subplot(111)
    ax1.set_title('Normalized difference compared to reference')
    ax1.set_ylabel('True positive rate')
    ax1.set_xlabel('False positive rate')
    pU.putAvaNameOnPlot(ax1, cfgPath['projectName'])
    if plotDensity:  # estimate 2D histogram --> create pcolormesh
        nbins = 100
        H, xedges, yedges = np.histogram2d(rFP, rTP, bins=nbins)
        H = np.flipud(np.rot90(H))
        Hmasked = np.ma.masked_where(H == 0, H)
        dataDensity = plt.pcolormesh(xedges, yedges, Hmasked, cmap=cm.cool)
        cbar = plt.colorbar(dataDensity, orientation='horizontal')
        cbar.ax.set_ylabel('hit rate density')
    else:
        for k in range(len(rTP)):
            pfarbe = color[k+1]  # colorvar(float(k), len(rTP), colorflag)
            if k == 0:
                ax1.plot(rFP[k], rTP[k], color='g', label='Reference', marker='+',
                         markersize=2*pU.ms, linestyle='None')
            elif k == 1:
                ax1.plot(rFP[k], rTP[k], marker=pU.markers, label='sims',
                         color=pfarbe, linestyle='None')
            else:
                ax1.plot(rFP[k], rTP[k], marker=pU.markers,
                         color=pfarbe, linestyle='None')
            mk = mk+1
            if mk == len(pU.markers):
                mk = 0
        ax1.legend(loc=4)

    plt.xlim([-0.03, max(1, max(rFP)+0.03)])
    plt.ylim([-0.03, 1.03])
    plt.grid('on')

    #outFileName = '_'.join([cfgPath['projectName'], cfgPath['dirName'],
    #                    'plim', str(int(plim)), 'ROC'])
    outFileName = '_'.join([cfgPath['projectName'],
                        'plim', str(int(plim)), 'ROC'])

    pU.saveAndOrPlot(cfgPath, cfgFlags, outFileName, fig)

    return
