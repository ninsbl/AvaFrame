"""
    Generate a markdown report for data provided in dictionary with format to compare two simulations
"""

# Load modules
import os
import glob
import logging
import numpy as np
import shutil
from avaframe.in3Utils import fileHandlerUtils as fU

# create local logger
# change log level in calling module to DEBUG to see log messages
log = logging.getLogger(__name__)


def copyQuickPlots(avaName, testName, outDir, plotListRep, rel):
    """ copy the quick plots to report directory """

    plotPaths = {}
    for key in plotListRep:
        plotName =  os.path.join(outDir, '%s_%s_%s.png' % (testName, rel, key))
        shutil.copy2(plotListRep[key], plotName)
        log.debug('Copied: %s to %s' % (plotListRep[key], plotName))
        plotPaths[key] = plotName

    return plotPaths

def copyAimecPlots(plotFiles , testName, outDir, plotPaths):
    """ copy the quick plots to report directory """

    for pFile in plotFiles:
        name = os.path.basename(pFile)
        plotName =  os.path.join(outDir, '%s_%s.png' % (testName, name))
        shutil.copy2(pFile, plotName)
        log.info('Copied: %s to %s' % (pFile, plotName))
        plotPaths[name] = plotName

    return plotPaths

def makeLists(simDict, benchDict):
    """ Create a list for table creation """

    parameterList = []
    valuesSim = []
    valuesBench = []
    for key in simDict:
        if key != 'type':
            if simDict[key] == '' and benchDict.get(key) is None:
                log.debug('this parameter is not used: %s' % key)
            else:
                parameterList.append(key)
                valuesSim.append(simDict[key])
                if key in benchDict:
                    valuesBench.append(benchDict[key])
                else:
                    valuesBench.append('non existent')

    return parameterList, valuesSim, valuesBench


def writeCompareReport(reportFile, reportD, benchD, avaName, cfgRep):
    """ Write a report in markdown format of the comparison of simulations to reference simulation results;
        report is saved to location of reportFile


        Parameters
        ----------
        reportFile : str
            path to report file
        reportD : dict
            report dictionary with simulation info
        benchD : str
            dictionary with simulation info of refernce simulation
        avaName : str
            name of avalanche
        cfgRep : dict
            dictionary with configuration info
    """

    # Set limit to produce warning for differences in peak fields
    diffLim = float(cfgRep['GENERAL']['diffLim'])

    # Start writing markdown style report
    with open(reportFile, 'a') as pfile:

        # HEADER BLOCK
        # Simulation name
        pfile.write('## *%s* \n' % avaName)
        simName = reportD['simName']['name']
        pfile.write('### Simulation name: *%s* \n' % reportD['simName']['name'])
        if benchD['simName'] != simName:
            textString = '<span style="color:red"> Reference simulation name is different: \
                         %s  </span>' % benchD['simName']
            pfile.write('#### %s \n' % textString)
        pfile.write(' \n')

        # TEST Info
        pfile.write('#### Test Info \n')
        pfile.write(' \n')
        for value in benchD['Test Info']:
            if value != 'type':
                # pfile.write('##### Topic:  %s \n' % value)
                pfile.write('%s \n' % (benchD['Test Info'][value]))
                pfile.write(' \n')

        # Create lists to write tables
        parameterList, valuesSim, valuesBench = makeLists(reportD['Simulation Parameters'], benchD['Simulation Parameters'])

        # PARAMETER BLOCK
        # Table listing all the simulation parameters
        pfile.write('#### Simulation Parameters \n')
        pfile.write(' \n')
        pfile.write('| Parameter | Reference | Simulation | \n')
        pfile.write('| --------- | --------- | ---------- | \n')
        countValue = 0
        for value in parameterList:
            # if reference and simulation parameter value do not match
            # mark red
            if valuesBench[countValue] != valuesSim[countValue]:
                valueRed = '<span style="color:red"> %s </span>' % valuesSim[countValue]
                pfile.write('| %s | %s | %s | \n' % (value, valuesBench[countValue], valueRed))
                countValue = countValue + 1
            else:
                pfile.write('| %s | %s | %s | \n' % (value, valuesBench[countValue], valuesSim[countValue]))
                countValue = countValue + 1

        # Add time needed for simulation to table
        pfile.write('| Run time [s] |  | %.2f | \n' % (reportD['runTime']))
        pfile.write(' \n')
        pfile.write(' \n')

        # IMAGE BLOCK
        pfile.write('#### Comparison Plots \n')
        pfile.write(' \n')
        for value in reportD['Simulation Results']:
            if value != 'type':
                pfile.write('##### Figure:   %s \n' % value)
                pfile.write(' \n')
                if value == 'ppr' or value == 'pfd' or value == 'pfv':
                    maxDiff = max(abs(float(reportD['Simulation Difference'][value][2])),
                                     abs(float(reportD['Simulation Difference'][value][0])))
                    maxVal = float(reportD['Simulation Stats'][value][0])
                    if maxDiff < (-1.0*diffLim*maxVal) or maxDiff > (diffLim*maxVal):
                        textString1 = '<span style="color:red"> Warning absolute difference exceeds the tolerance of %.0f percent of %s-max value (%.2f) </span>' % (100.*diffLim, value, maxVal)
                        textString2 = '<span style="color:red"> Difference is: Max = %0.2f, Mean = %.02f and Min = %.02f </span>' % (reportD['Simulation Difference'][value][0],
                                     reportD['Simulation Difference'][value][1], reportD['Simulation Difference'][value][2])
                        pfile.write(' %s \n' % textString1)
                        pfile.write(' %s \n' % textString2)
                        pfile.write(' \n')
                pfile.write('![%s](%s) \n' % (value, reportD['Simulation Results'][value]))
                pfile.write(' \n')
                pfile.write(' \n')

        pfile.write(' \n')
        pfile.write('------------------------------------------------------------------------- \n')
        pfile.write(' \n')
        pfile.write(' \n')

    log.info('Standard tests performed - Report saved to: %s ' % reportFile)
