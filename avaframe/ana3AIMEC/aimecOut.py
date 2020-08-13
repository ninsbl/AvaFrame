import os
import logging
import math
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import cm

# Local imports
import avaframe.in2Trans.shpConversion as shpConv
import avaframe.in2Trans.geoTrans as geoTrans
import avaframe.in3Utils.ascUtils as IOf


# create local logger
log = logging.getLogger(__name__)

# -----------------------------------------------------------
# result_write
# -----------------------------------------------------------


def result_write(data_name, data, outfile, header):
    """
    This function is used as standart output file

    example path: 'log/doublestep_5_5m_calibration_results.txt'
    example header: 'runout, maxvel, rho, mu, tau_0, R_s^0, kappa, R, B, q \n'

    INPUT: data, path, header
    """

#    chekc if folder exists / create
    if not os.path.exists(os.path.dirname(outfile)):
        os.makedirs(os.path.dirname(outfile))

    output = data
    fid = open(outfile, 'w')
    fid.write(header)
    for i in range(len(output[0])):
        tmp = os.path.basename(data_name[i])
#        name = tmp.split('.')[0] # CoSiCa-Samos
        name = os.path.splitext(tmp)[0]  # DAKUMO
        fid.write('%s' % name)
        for j in range(len(output)):
            try:
                fid.write(',%5.2f' % output[j][i])
            except:
                fid.write(',NaN')
        fid.write('\n')
    fid.close()

    log.info('File written: %s' % outfile)

# -----------------------------------------------------------
# colorvar
# -----------------------------------------------------------


def colorvar(k, k_end, colorflag, disp=0):
    """
    jt colorvariation editor - JT 2012
    determine how color changes from runnumber = 1 to runnumber = runlength
    input: runnumber,runlength,colorflag,verbose
    output: [R G B]

    possible colorflags:
    'ry': red to yellow
    'bb': blue to light blue
    'pw': pink to white
    'kg' black to green
    'bp' blue to pink
    'pb' pink to blue
    'gy' green to yellow
    'cw' cyan to white
    'kr' black to red
    'gb' green to blue
    'rp' red to pink
    'yw' yellow to white
    'kb' black to blue
    'kc' black to cyan
    'kp' black to pink
    'kw' black to white
    """

    colors = {
        'ry': [1., k/k_end, 0.],  # rot zu gelb
        'bb': [0., k/k_end, 1.],  # blau zu hellbalu
        'pw': [0.8, k/k_end, 0.8],  # pink zu weiss
        'kg': [0., k/k_end, 0.],  # schwarz zu gruen
        'bp': [k/k_end, 0., 1.],  # blau zu pink
        'pb': [1.-k/k_end, 1., 0.],  # blau zu pink
        'gy': [k/k_end, 1., 0.],  # green zu yellow
        'cw': [k/k_end, 1., 1.],  # cyan zu weiss
        'kr': [k/k_end, 1., 1.],  # black to red
        'gb': [0., 1., k/k_end],  # gruen zu blau
        'rp': [1., 0., k/k_end],  # rot zu pink
        'yw': [1., 1., k/k_end],  # yellow to white
        'kb': [0., 0., k/k_end],  # black tp blue
        'kc': [0., k/k_end, k/k_end],  # black zu cyan
        'kp': [k/k_end, 0., k/k_end],  # black zu pink
        'kw': [1.-k/k_end, 1.-k/k_end, 1.-k/k_end]  # black to white
    }

    colornames = {
        'ry': 'red to yellow',
        'bb': 'blue to cyan',
        'pw': 'pink to white',
        'kg': 'black to green',
        'bp': 'blue to pink',
        'pb': 'blue to pink',
        'gy': 'green to yellow',
        'cw': 'cyan to white',
        'kr': 'black to red',
        'gb': 'green to blue',
        'rp': 'rot to pink',
        'yw': 'yellow to white',
        'kb': 'black to blue',
        'kc': 'black to cyan',
        'kp': 'black to pink',
        'kw': 'black to white'
    }

    if colorflag.lower() in colors:
        farbe = colors.get(colorflag.lower())
        if k == 0:
            log.info('Color is: %s' % colornames.get(colorflag.lower()))
    else:
        farbe = [0, 0, 0]
        if k == 0:
            log.info('Color is black')

    return farbe

# -----------------------------------------------------------
# result_visu
# -----------------------------------------------------------


def result_visu(fnames, rasterSource, ProfileLayer, runout, mean_max_dpp,
                max_max_dpp, doku, GI, dpp_threshold, outpath, DefaultName=None):
    """
    Visualize results in a nice way
    Jan-Thomas Fischer BFW 2010-2012
    AK BFW 2014-2015
    """
    cvar = ['ry', 'bb', 'pw', 'gy']
    colorflag = cvar[0]

    figure_width = 7*2
    figure_height = 4*2
    fs = 20
    mks = 10
    lw = 2
    # includes flag for y axis -
    # 1 = rddp
    # 2 = frontal shape
    # 3 = groth index
    # 4 = runout for intrapraevent
    # 5 = pressure data
    flag = 3
    if (len(fnames) > 100):
        plot_density = 1
    else:
        plot_density = 0

    if flag == 1:
        log.info('Visualizing pressure data')
        tipo = 'rapp'
        data = mean_max_dpp / mean_max_dpp[0]
        yaxis_label = 'rAPP [-]'
        ytick_increment = 0.25
        ymax = 3
    elif flag == 2:
        log.info('Visualizing EGU growth index data')
        tipo = 'GI'
        data = GI
        yaxis_label = 'growth index [GI]'
        ytick_increment = 2
    elif flag == 3:
        log.info('Visualizing pressure data')
        tipo = 'rmpp'
        data = max_max_dpp / max_max_dpp[0]
        yaxis_label = 'rMPP [-]'
        ytick_increment = 0.1
#        ymax = 0.12
#        ymin = 0.08
#        ymax = 0.5
#        ymin = 0.3
        ymax = max(data[1:])+(max(data[1:])-min(data[1:]))*0.1
        ymin = min(data[1:])-(max(data[1:])-min(data[1:]))*0.1
    else:
        log.error('Wrong flag')
        return None

    # read data
    dem = IOf.readRaster(rasterSource)
    header = dem['header']
    xllcenter = header.xllcenter
    yllcenter = header.yllcenter
    cellsize = header.cellsize

    rasterdata = dem['rasterdata']

    Avapath = shpConv.readLine(ProfileLayer, DefaultName, dem['header'])
    AvaProfile, SplitPoint, splitPoint = geoTrans.prepareLine(
        dem, Avapath, splitPoint=None, distance=10)
    x_path = AvaProfile['x']
    y_path = AvaProfile['y']
    z_path = AvaProfile['z']
    s_path = AvaProfile['s']

    xlim_prof_axis = max(s_path) + 50

    # Final result diagram - z_profile+data
    fig = plt.figure(figsize=(figure_width, figure_height), dpi=300)

    markers = ['+', 'o', 'x', '*', 's', 'd', '^', 'v', '>', '<', 'p', 'h', '.',
               '^', 'v', '>', '<', 'p', 'h', '.']
    mk = 0

#    show flow path
    ax1 = fig.add_subplot(111)
#    plt.xlim([0, xlim_prof_axis])
#    plt.ylim([0, math.ceil(max(data)+0.25)])
#    plt.ylim([0, ymax])
#    plt.yticks(np.arange([0, math.ceil(max(data)+0.25), ytick_increment]))
    ax1.set_ylabel(yaxis_label, color='b', fontsize=2*fs)
    ax1.set_xlabel(''.join(['s [m] - runout with ', str(dpp_threshold),
                            ' kPa threshold']), color='black', fontsize=2*fs)
    if plot_density:  # estimate 2D histogram --> create pcolormesh
        nbins = 100
        H, xedges, yedges = np.histogram2d(runout, data, bins=nbins)
        H = np.flipud(np.rot90(H))
        Hmasked = np.ma.masked_where(H == 0, H)
        data_density = plt.pcolormesh(xedges, yedges, Hmasked, cmap=cm.Blues)
#        data_density = plt.pcolormesh(xedges, yedges, Hmasked, cmap=cm.cool)
        cbar = plt.colorbar(data_density, orientation='horizontal')
        cbar.ax.set_ylabel('Counts')
    ax2 = ax1.twinx()
    ax2.set_ylabel('z [m]', color='g', fontsize=2*fs)
    ax2.plot(s_path, z_path, color='green', label='path', linestyle='--', linewidth=2*lw)
    plt.xlim([0, xlim_prof_axis])
    plt.ylim([math.floor(min(z_path)/10)*10, math.ceil(max(z_path)/10)*10])
    if not plot_density:
        for k in range(len(runout)):
            topo_name = fnames[k].split('/')[-1]
            pfarbe = colorvar(float(k), len(runout), colorflag)
            if k == 0:
                ax1.plot(runout[k], data[k], marker='+',
                         markersize=2*mks, color='g', label=topo_name)
    #            plt.yticks(np.arange([0,5000,250]))
                # Make the y-tick labels of first axes match the line color.
                for tl in ax1.get_yticklabels():
                    tl.set_color('b')
            else:
                ax1.plot(runout[k], data[k], label=topo_name, marker=markers[mk],
                         markersize=mks, color=pfarbe, linewidth=lw)
            mk = mk+1
            if mk == len(markers):
                mk = 1
    plt.grid('on')
#    plt.legend()
#    ax1.legend(loc=0)
#    ax2.legend(loc=0)

    pro_name = fnames[0].split('/')[-3]
    outname_fin = ''.join([outpath, '/pics/', pro_name, '_dptr',
                           str(int(dpp_threshold)), '_', tipo, '.pdf'])

    if not os.path.exists(os.path.dirname(outname_fin)):
        os.makedirs(os.path.dirname(outname_fin))
    fig.savefig(outname_fin, transparent=True)

    plt.close(fig)

    # Final result diagram - roc-plots
    rTP = (np.array(doku[0]) / (float(doku[0][0]) + float(doku[1][0]))).astype(float)
    rFP = (np.array(doku[2]) / (float(doku[2][0]) + float(doku[3][0]))).astype(float)


#    rFP = (np.array(doku[2]) / (float(doku[0][0]) + float(doku[1][0]))).astype(float)

    fig = plt.figure(figsize=(figure_width, figure_height), dpi=300)

    mk = 0
    ax1 = fig.add_subplot(111)
    ax1.set_ylabel('True positive rate', fontsize=2*fs)
    ax1.set_xlabel('False positive rate', fontsize=2*fs)
    if plot_density:  # estimate 2D histogram --> create pcolormesh
        nbins = 100
        H, xedges, yedges = np.histogram2d(rFP, rTP, bins=nbins)
        H = np.flipud(np.rot90(H))
        Hmasked = np.ma.masked_where(H == 0, H)
#        data_density = plt.pcolormesh(xedges, yedges, Hmasked, cmap=cm.Blues)
        data_density = plt.pcolormesh(xedges, yedges, Hmasked, cmap=cm.cool)
        cbar = plt.colorbar(data_density, orientation='horizontal')
        cbar.ax.set_ylabel('hit rate density')
    if not plot_density:
        for k in range(len(rTP)):
            topo_name = fnames[k].split('/')[-1]
            pfarbe = colorvar(float(k), len(rTP), colorflag)
            ax1.plot(rFP[k], rTP[k], label=topo_name, marker=markers[mk],
                     markersize=mks, color=pfarbe, linewidth=lw)
            mk = mk+1
            if mk == len(markers):
                mk = 0
    plt.xlim([0, max(1, max(rFP))])
    plt.ylim([0, 1])
    plt.grid('on')

    outname_fin = ''.join([outpath, '/pics/', pro_name, '_dptr',
                           str(int(dpp_threshold)), '_ROC.pdf'])

    if not os.path.exists(os.path.dirname(outname_fin)):
        os.makedirs(os.path.dirname(outname_fin))
    fig.savefig(outname_fin, transparent=True)

    plt.close(fig)

    return
