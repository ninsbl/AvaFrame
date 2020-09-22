"""
    Plot settings for output figures

    This file is part of Avaframe.
"""

import seaborn as sns
from matplotlib import cm
import copy
import matplotlib
import cmocean
import copy

from avaframe.out3SimpPlot.makePalette import *


# define seaborn style and color maps
sns.set(font_scale=1)
sns.set_style("ticks", {'axes.linewidth': 1, 'axes.edgecolor':'black',  'font.family': ['serif']})
# print(sns.axes_style())


# define figure dimentions
figW = 6
figH = 6
# define lines and marker properties
lw = 1.5
ms = 5
markers = 'o'
matplotlib.rcParams['lines.linewidth'] = lw
matplotlib.rcParams['lines.markersize'] = ms
# font size
fs = 12
matplotlib.rcParams['figure.titlesize'] = 'xx-large'
matplotlib.rcParams['axes.labelsize'] = 'x-large'
# set output extension {png, ps, pdf, svg}
matplotlib.rcParams["savefig.format"] = 'png'
# define figure resolution (dpi)
matplotlib.rcParams['figure.dpi'] = 150

matplotlib.rcParams['text.usetex'] = True
matplotlib.rcParams['figure.autolayout'] = True


############################
###### Color maps ##########
############################
# hell white/green to dark blue
cmapGB = copy.copy(sns.cubehelix_palette(8, start=.5, rot=-.75, as_cmap=True))
cmapGB.set_bad(color='k')
# hell pink to dark purple
cmapPP = copy.copy(sns.cubehelix_palette(8, as_cmap=True))
cmapPP.set_bad(color='k')

cmapReds = copy.copy(matplotlib.cm.Reds)
cmapReds.set_bad(color='k')
cmapBlues = copy.copy(matplotlib.cm.Blues)
cmapBlues.set_bad(color='k')

cmapGreys = copy.copy(matplotlib.cm.get_cmap("Greys"))

cmapjet = copy.copy(matplotlib.cm.jet)
cmapjet.set_bad(color='k')
cmapPlasma = copy.copy(matplotlib.cm.plasma)
cmapPlasma.set_bad(color='k')
cmapViridis = copy.copy(matplotlib.cm.viridis)
cmapViridis.set_bad(color='k')

cmapIce = copy.copy(cmocean.cm.ice)
cmapIce.set_bad(color='k')

cmapDense = copy.copy(cmocean.cm.dense)
cmapDense.set_bad(color='k')

# divergent color map
cmapdiv = copy.copy(matplotlib.cm.RdBu_r) #sns.color_palette("RdBu_r")



colorAvaframe = ['#0EF8EA', '#12E4E6', '#28D0DF', '#3CBCD5', '#4AA8C9', '#5595B9', '#5C82A8', '#5F6F95', '#5E5E81', '#5A4D6C', '#523E58', '#483045']
cmapAvaframe = get_continuous_cmap(colorAvaframe)
cmapAvaframe.set_bad(color='k')
cmapAimec = cmapAvaframe

cmapPres =  cmapViridis
cmapDepth = cmapBlues
cmapSpeed = cmapReds
cmapDEM = cmapGreys


cmapPres, colors  = makeColorMap()
cmapPres = cmapAvaframe
cmapPres.set_bad(color='k')
