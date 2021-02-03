
import numpy as np
import time
import math
import matplotlib.pyplot as plt

# Local imports
import avaframe.in2Trans.ascUtils as IOf
import avaframe.out3Plot.plotUtils as pU
import avaframe.com1DFAPy.DFAtools as DFAtls
import avaframe.com1DFAPy.com1DFA as com1DFA
# import avaframe.com1DFAPy.SPHfunctions as SPH
from avaframe.in3Utils import cfgUtils
import avaframe.com1DFAPy.DFAfunctionsCython as DFAfunC
cfg = cfgUtils.getModuleConfig(com1DFA)['GENERAL']
cfgFull = cfgUtils.getModuleConfig(com1DFA)

########################################################################
# CHOOSE YOUR SETUP
##########################################################################
# Choose the snow depth you want to use (h function)


def Hfunction(x, y, z):
    # h = x*x/1000 + 1
    GHx = 2*x*y/10000
    GHy = x*x/10000
    h = x*x*y/10000 + 1
    # r = np.sqrt((x-12.5)*(x-12.5)+(y-12.5)*(y-12.5))
    # H0 = 1
    # h = H0 * (1 - (r/12.5) * (r/12.5))
    GHz = np.zeros(np.shape(x))
    return h, GHx, GHy, GHz


# Choose the surface shape you want to use
def Sfunction(x, y, Lx, Ly):
    # plane
    Z = x*np.tan(slopeAnglex) + y*np.tan(slopeAngley)
    sx = np.tan(slopeAnglex)*np.ones(np.shape(x))
    sy = np.tan(slopeAngley)*np.ones(np.shape(x))
    area = np.sqrt(1 + (np.tan(slopeAnglex))*(np.tan(slopeAnglex)) + (np.tan(slopeAngley))*(np.tan(slopeAngley)))*np.ones(np.shape(x))
    return Z, sx, sy, area


slopeAnglex = 0*math.pi/180
slopeAngley = 0*math.pi/180
# set the size of the mesh grid [m]
NDX = 5
# choose the number of particles per DX and DY
# if you choose 3, you will have 3*3 = 9 particles per grid cell
NPartPerD = [2, 3, 4, 5, 6]

# choose if the particles should be randomly distributed.
# 0 no random part, up to 1, random fluctuation of dx/2 and dy/2
coef = 0.5
rho = 200
##############################################################################
# END CHOOSE SETUP
###############################################################################


def definePart(dx, dy, Lx, Ly):
    # define particles
    nx = np.int(Lx/dx)-1
    ny = np.int(Ly/dy)-1
    Npart = nx*ny
    x = np.linspace(dx, Lx-dx, nx)
    y = np.linspace(dy, Ly-dy, ny)
    xx, yy = np.meshgrid(x, y)
    xx = xx.flatten()
    yy = yy.flatten()
    Xpart = xx + (np.random.rand(Npart) - 0.5) * dx * coef
    Ypart = yy + (np.random.rand(Npart) - 0.5) * dy * coef
    # adding z component
    Zpart, sx, sy, area = Sfunction(Xpart, Ypart, Lx, Ly)
    Hpart, _, _, _ = Hfunction(Xpart, Ypart, Zpart)
    Mpart = Hpart * dx * dy * area * rho
    # create dictionnary to store particles properties
    particles = {}
    particles['Npart'] = Npart
    particles['mTot'] = np.sum(Mpart)
    particles['x'] = Xpart
    particles['y'] = Ypart
    particles['z'] = Zpart
    particles['s'] = np.zeros(np.shape(Ypart))
    particles['ux'] = np.zeros(np.shape(Ypart))
    particles['uy'] = np.zeros(np.shape(Ypart))
    particles['uz'] = np.zeros(np.shape(Ypart))
    particles['m'] = Mpart
    particles['h'] = Hpart
    return particles


def defineGrid(Lx, Ly, csz):
    # define grid
    NX = np.int(Lx/csz + 1)
    NY = np.int(Ly/csz + 1)
    header = IOf.cASCheader()
    header.ncols = NX
    header.nrows = NY
    header.cellsize = csz
    dem = {}
    dem['header'] = header
    X = np.linspace(0, Lx, NX)
    Y = np.linspace(0, Ly, NY)
    XX, YY = np.meshgrid(X, Y)
    ZZ, _, _, _ = Sfunction(XX, YY, Lx, Ly)
    dem['rasterData'] = ZZ
    # Initialize mesh
    dem = com1DFA.initializeMesh(dem, num=4)

    Dummy = np.zeros((NY, NX))
    fields = {}
    fields['pfv'] = Dummy
    fields['ppr'] = Dummy
    fields['pfd'] = Dummy
    fields['V'] = Dummy
    fields['P'] = Dummy
    fields['FD'] = Dummy
    return dem, fields


def plotFD(ax, x, xx, h, particles, ind, mark, count):
    if count == 1:
        ax.plot(xx, h, color='r', linestyle='-', label='real flow depth')
    ax.plot(particles[x][ind], particles['h2'][ind], color='b',
             marker=mark, linestyle='None', label='corrected flow depth' + str(nPartPerD))
    ax.plot(particles[x][ind], particles['h1'][ind], color='g',
             marker=mark, linestyle='None', label='flow depth')
    # ax.plot(particles[x][ind], particles['h2'][ind], color='c',
    #          marker=mark, linestyle='None', label='half corrected flow depth')
    ax.plot(particles[x][ind], particles['h'][ind], color='k',
             marker=mark, linestyle='None', label='flow depth bilinear')
    return ax


def plotGrad(ax, x, xx, particles, ind, mark, count):
    if count == 1:
        ax.plot(xx, gx, color='r', linestyle='-', label='real gradHX')
        ax.plot(xx, gy, color='g', linestyle='-', label='real gradHY')
        ax.plot(xx, gz, color='k', linestyle='-', label='real gradHZ')

    ax.plot(particles[x][ind], GHX[ind], color='m', marker=mark, markersize=5,
             linestyle='None', label='SPH N=' + str(nPartPerD))
    ax.plot(particles[x][ind], GHY[ind], color='m', marker=mark, markersize=5,
             linestyle='None')
    ax.plot(particles[x][ind], GHZ[ind], color='m', marker=mark, markersize=5,
             linestyle='None')
    ax.plot(particles[x][ind], GHX2[ind], color='c', marker=mark, markersize=5,
             linestyle='None', label='Corrected SPH N=' + str(nPartPerD))
    ax.plot(particles[x][ind], GHY2[ind], color='c', marker=mark, markersize=5,
             linestyle='None')
    ax.plot(particles[x][ind], GHZ2[ind], color='c', marker=mark, markersize=5,
             linestyle='None')
    ax.plot(particles[x][ind], GHX4[ind], color='y', marker=mark, markersize=5,
             linestyle='None', label='Corrected full SPH N=' + str(nPartPerD))
    ax.plot(particles[x][ind], GHY4[ind], color='y', marker=mark, markersize=5,
             linestyle='None')
    ax.plot(particles[x][ind], GHZ4[ind], color='y', marker=mark, markersize=5,
             linestyle='None')
    return ax


fig1, ax1 = plt.subplots(figsize=(2*pU.figW, pU.figH))
ax1.set_title('h(x)')
ax1.set_xlabel('x [m]')
ax1.set_ylabel('h [m]')
fig2, ax2 = plt.subplots(figsize=(2*pU.figW, pU.figH))
ax2.set_title('h(y)')
ax2.set_xlabel('y [m]')
ax2.set_ylabel('h [m]')
fig3, ax3 = plt.subplots(figsize=(2*pU.figW, pU.figH))
ax3.set_title('Gradh(x)')
ax3.set_xlabel('x [m]')
ax3.set_ylabel('Gradh []')
fig4, ax4 = plt.subplots(figsize=(2*pU.figW, pU.figH))
ax4.set_title('Gradh(y)')
ax4.set_xlabel('y [m]')
ax4.set_ylabel('Gradh []')

markers = ['o', 's', 'd', '*', 'p', 'P', '^', '>', '<', 'X', 'h']
count = 0

csz = NDX
nCells = 10

# set the extend of your mesh
Lx = nCells*csz
Ly = nCells*csz

for nPartPerD in NPartPerD:
    dx = csz/nPartPerD
    dy = csz/nPartPerD

    # ------------------------------------------
    # define particles
    particles = definePart(dx, dy, Lx, Ly)
    Htrue = particles['h']
    # ------------------------------------------
    # define grid
    dem, fields = defineGrid(Lx, Ly, csz)

    # ------------------------------------------
    # find neighbours
    particles = DFAfunC.getNeighboursC(particles, dem)
    particles, fields = DFAfunC.updateFieldsC(cfg, particles, dem, fields)

    # ------------------------------------------
    # Compute SPH gradient
    header = dem['header']
    Nx = dem['Nx']
    Ny = dem['Ny']
    Nz = dem['Nz']
    indPartInCell = (particles['indPartInCell']).astype('int')
    partInCell = (particles['partInCell']).astype('int')
    indX = particles['indX'].astype('int')
    indY = particles['indY'].astype('int')

    startTime = time.time()
    GHX, GHY, GHZ = DFAfunC.computeGradC(cfg, particles, header, Nx, Ny, Nz, indX, indY, SPHOption=1, gradient=1)
    GHX = np.asarray(GHX)
    GHY = np.asarray(GHY)
    GHZ = np.asarray(GHZ)
    tottime = time.time() - startTime
    print('Time SPHOption 1: ', tottime)

    startTime = time.time()
    GHX2, GHY2, GHZ2 = DFAfunC.computeGradC(cfg, particles, header, Nx, Ny, Nz, indX, indY, SPHOption=2, gradient=1)
    GHX2 = np.asarray(GHX2)
    GHY2 = np.asarray(GHY2)
    GHZ2 = np.asarray(GHZ2)
    particles['gradx'] = GHX2
    particles['grady'] = GHY2
    particles['gradz'] = GHZ2
    tottime = time.time() - startTime
    print('Time SPHOption 2: ', tottime)

    startTime = time.time()
    startTime = time.time()
    GHX4, GHY4, GHZ4 = DFAfunC.computeGradC(cfg, particles, header, Nx, Ny, Nz, indX, indY, SPHOption=4, gradient=1)
    GHX4 = np.asarray(GHX4)
    GHY4 = np.asarray(GHY4)
    GHZ4 = np.asarray(GHZ4)
    tottime = time.time() - startTime
    print('Time SPHOption 4: ', tottime)

    startTime = time.time()
    # Compute sph FD
    H, C, W = DFAfunC.computeFDC(cfg, particles, header, Nx, Ny, Nz, indX, indY)
    H = np.asarray(H)
    W = np.asarray(W)
    C = np.asarray(C)
    particles['hSPH'] = H
    particles['W'] = W
    particles['h1'] = H
    particles['h2'] = H/W
    # particles['h3'] = (H-C)/W
    tottime = time.time() - startTime
    print('Time FD: ', tottime)

    # ------------------------------------------------------
    # Post processing

    m = particles['m']
    x = particles['x']
    y = particles['y']
    z = particles['z']
    h, Ghx, Ghy, Ghz = Hfunction(particles['x'], particles['y'], particles['z'])

    count = count + 1
    mark = markers[count-1]
    ind = np.where(((y > Ly/2-0.5*dy) & (y < Ly/2+0.5*dy)))
    xx = np.linspace(0, Lx, 100)
    yy = Ly/2*np.ones(100)
    zz = np.zeros(100)
    h, gx, gy, gz = Hfunction(xx, yy, zz)
    ax1 = plotFD(ax1, 'x', xx, h, particles, ind, mark, count)
    ax3 = plotGrad(ax3, 'x', xx, particles, ind, mark, count)

    ind = np.where(((x > Lx/2-0.5*dx) & (x < Lx/2+0.5*dx)))
    yy = np.linspace(0, Ly, 100)
    xx = Lx/2*np.ones(100)
    zz = np.zeros(100)
    h, gx, gy, gz = Hfunction(xx, yy, zz)
    ax2 = plotFD(ax2, 'y', yy, h, particles, ind, mark, count)
    ax4 = plotGrad(ax4, 'y', yy, particles, ind, mark, count)

fig1.legend()
fig2.legend()
fig3.legend()
fig4.legend()
plt.show()
