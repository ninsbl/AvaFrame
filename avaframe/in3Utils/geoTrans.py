"""
    Opperations and transformations of rasters and lines

    This file is part of Avaframe.
"""

import math
import numpy as np
import copy
import logging


# create local logger
log = logging.getLogger(__name__)


def projectOnRaster(dem, Points, interp='bilinear'):
    """ Projects the points Points on Raster using a bilinear or nearest
    interpolation and returns the z coord (for loop on points)
    Input :
    Points: list of points (x,y) 2 rows as many columns as Points
    Output:
    PointsZ: list of points (x,y,z) 3 rows as many columns as Points
    """
    header = dem['header']
    Z = dem['rasterData']
    xllc = header.xllcenter
    yllc = header.yllcenter
    csz = header.cellsize
    xcoor = Points['x']
    ycoor = Points['y']
    zcoor = np.array([])
    for i in range(np.shape(xcoor)[0]):
        value = projectOnRasterRoot(xcoor[i], ycoor[i], Z, csz=csz, xllc=xllc,
                                    yllc=yllc, interp='bilinear')
        zcoor = np.append(zcoor, value)

    Points['z'] = zcoor
    return Points


def projectOnRasterRoot(x, y, Z, csz=1, xllc=0, yllc=0, interp='bilinear'):
    """ Projects one point on Raster using a bilinear or nearest
    interpolation and returns the z coord
    Input :
    Points: (x,y) coord of the point
    Output:
    PointsZ: z coord of the point
    """
    try:
        Lx = (x - xllc) / csz
        Ly = (y - yllc) / csz
        Lx0 = int(np.floor(Lx))
        Ly0 = int(np.floor(Ly))
        Lx1 = int(np.floor(Lx)) + 1
        Ly1 = int(np.floor(Ly)) + 1
        # prepare for bilinear interpolation(do not take out of bound into account)
        if interp == 'nearest':
            dx = np.round(Lx - Lx0)
            dy = np.round(Ly - Ly0)
        elif interp == 'bilinear':
            dx = Lx - Lx0
            dy = Ly - Ly0
        try:
            f11 = Z[Ly0][Lx0]
            f12 = Z[Ly1][Lx0]
            f21 = Z[Ly0][Lx1]
            f22 = Z[Ly1][Lx1]
            # using bilinear interpolation on the cell
            value = (f11*(1-dx)*(1-dy) + f21*dx*(1-dy) +
                     f12*(1-dx)*dy + f22*dx*dy)
        except IndexError:
            value = np.NaN
    except ValueError:
        value = np.NaN

    return value


def projectOnRasterVect(dem, Points, interp='bilinear'):
    """
    Vectorized version of projectOnRaster
    Projects the points Points on Raster using a bilinear or nearest
    interpolation and returns the z coord (no for loop)
    Input :
    Points: list of points (x,y) 2 rows as many columns as Points
    Output:
    PointsZ: list of points (x,y,z) 3 rows as many columns as Points

    """
    header = dem['header']
    rasterdata = dem['rasterData']
    xllc = header.xllcenter
    yllc = header.yllcenter
    cellsize = header.cellsize
    xcoor = Points['x']
    ycoor = Points['y']
    zcoor = np.array([])

    zcoor, ioob = projectOnRasterVectRoot(xcoor, ycoor, rasterdata,
                                                csz=cellsize, xllc=xllc,
                                                yllc=yllc, interp=interp)
    Points['z'] = zcoor
    return Points, ioob


def projectOnRasterVectRoot(x, y, Z, csz=1, xllc=0, yllc=0, interp='bilinear'):
    """
    Vectorized version of projectOnRaster
    Projects the points Points on Raster using a bilinear or nearest
    interpolation and returns the z coord
    Input :
    Points: (x, y) coord of the pointsi
    Output:
    PointsZ: z coord of the points
             ioob number of out of bounds indexes
    """
    nrow, ncol = np.shape(Z)
    # initialize outputs
    z = np.ones((np.shape(x)))*np.NaN
    dx = np.ones((np.shape(x)))*np.NaN
    dy = np.ones((np.shape(x)))*np.NaN
    f11 = np.ones((np.shape(x)))*np.NaN
    f12 = np.ones((np.shape(x)))*np.NaN
    f21 = np.ones((np.shape(x)))*np.NaN
    f22 = np.ones((np.shape(x)))*np.NaN

    # find coordinates in normalized ref (origin (0,0) and cellsize 1)
    Lxx = (x - xllc) / csz
    Lyy = (y - yllc) / csz
    Lx = copy.deepcopy(Lxx)
    Ly = copy.deepcopy(Lyy)

    # find out of bound indexes
    Lx[np.where((Lxx < 0))] = np.NaN
    Ly[np.where((Lxx < 0))] = np.NaN
    Lx[np.where(Lxx >= (ncol-1))] = np.NaN
    Ly[np.where(Lxx >= (ncol-1))] = np.NaN
    Lx[np.where(Lyy < 0)] = np.NaN
    Ly[np.where(Lyy < 0)] = np.NaN
    Lx[np.where(Lyy >= (nrow-1))] = np.NaN
    Ly[np.where(Lyy >= (nrow-1))] = np.NaN

    # find index of index of not nan value
    mask = ~np.isnan(Lx+Ly)
    maskInd = np.argwhere(~np.isnan(Lx+Ly))[:, 0]
    itot = len(Lx)
    iinb = len(maskInd)
    ioob = itot - iinb

    # find coordinates of the 4 nearest cornes on the raster
    Lx0 = np.floor(Lx).astype('int')
    Ly0 = np.floor(Ly).astype('int')
    Lx1 = Lx0 + 1
    Ly1 = Ly0 + 1
    # prepare for bilinear interpolation(do not take out of bound into account)
    if interp == 'nearest':
        dx[mask] = np.round(Lx[mask] - Lx0[mask])
        dy[mask] = np.round(Ly[mask] - Ly0[mask])
    elif interp == 'bilinear':
        dx[mask] = Lx[mask] - Lx0[mask]
        dy[mask] = Ly[mask] - Ly0[mask]

    f11[mask] = Z[Ly0[mask], Lx0[mask]]
    f12[mask] = Z[Ly1[mask], Lx0[mask]]
    f21[mask] = Z[Ly0[mask], Lx1[mask]]
    f22[mask] = Z[Ly1[mask], Lx1[mask]]
    # using bilinear interpolation on the cell
    z = f11*(1-dx)*(1-dy) + f21*dx*(1-dy) + f12*(1-dx)*dy + f22*dx*dy

    return z, ioob


def pointsToRaster(x, y, z, Z, csz=1, xllc=0, yllc=0, interp='bilinear'):
    """
    Vectorized version of projectOnRaster
    Projects the points Points on Raster using a bilinear or nearest
    interpolation and returns the z coord
    Input :
    Points: (x, y) coord of the pointsi
    Output:
    PointsZ: z coord of the points
             ioob number of out of bounds indexes
    """
    nrow, ncol = np.shape(Z)

    # find coordinates in normalized ref (origin (0,0) and cellsize 1)
    Lx = (x - xllc) / csz
    Ly = (y - yllc) / csz

    # find coordinates of the 4 nearest cornes on the raster
    Lx0 = np.floor(Lx).astype('int')
    Ly0 = np.floor(Ly).astype('int')
    Lx1 = Lx0 + 1
    Ly1 = Ly0 + 1
    # prepare for bilinear interpolation(do not take out of bound into account)
    if interp == 'nearest':
        dx = np.round(Lx - Lx0)
        dy = np.round(Ly - Ly0)
    elif interp == 'bilinear':
        dx = Lx - Lx0
        dy = Ly - Ly0

    Z = Z.flatten()
    f11 = z*(1-dx)*(1-dy)
    f11 = f11.flatten()
    ic = Lx0 + ncol * Ly0
    # ic = Ly0 + ncol * Lx0
    np.add.at(Z, ic, f11)
    f21 = z*dx*(1-dy)
    f21 = f21.flatten()
    ic = Lx0 + ncol * Ly1
    # ic = Ly1 + ncol * Lx0
    np.add.at(Z, ic, f21)
    f12 = z*(1-dx)*dy
    f12 = f12.flatten()
    ic = Lx1 + ncol * Ly0
    # ic = Ly0 + ncol * Lx1
    np.add.at(Z, ic, f12)
    f22 = z*dx*dy
    f22 = f22.flatten()
    ic = Lx1 + ncol * Ly1
    # ic = Ly1 + ncol * Lx1
    np.add.at(Z, ic, f22)

    Z = np.reshape(Z, (nrow, ncol))

    return Z


def prepareLine(dem, avapath, distance=10, Point=None):
    """ 1- Resample the avapath line with a max intervall of distance=10m
    between points (projected distance on the horizontal plane).
    2- Make avalanche profile out of the path (affect a z value using the dem)
    3- Get projection of points on the profil (closest point)
    Inputs : - a dem dictionary
             - a avapath line dictionary
             - a resampling Distance
             - a point dictionary (optional, can contain several point)
    Outputs : - the resampled avaprofile
              - the projection of the point on the profile (if several points
              were give in input, only the closest point to the profile
              is projected)

    TODO: test
    """
    xcoor = avapath['x']
    ycoor = avapath['y']
    xcoornew = np.array([xcoor[0]])
    ycoornew = np.array([ycoor[0]])
    s = np.array([0])  # curvilinear coordinate allong the path
    # loop on the points of the avapath
    for i in range(np.shape(xcoor)[0] - 1):
        Vx = xcoor[i + 1] - xcoor[i]
        Vy = ycoor[i + 1] - ycoor[i]
        D = np.sqrt(Vx**2 + Vy**2)
        nd = int(np.floor(D / distance) + 1)
        # Resample each segment
        S0 = s[-1]
        for j in range(1, nd + 1):
            xn = j / (nd) * Vx + xcoor[i]
            yn = j / (nd) * Vy + ycoor[i]
            xcoornew = np.append(xcoornew, xn)
            ycoornew = np.append(ycoornew, yn)
            s = np.append(s, S0 + D * j / nd)

    ResampAvaPath = avapath
    ResampAvaPath['x'] = xcoornew
    ResampAvaPath['y'] = ycoornew
    ResampAvaPath = projectOnRaster(dem, ResampAvaPath)
    ResampAvaPath['s'] = s
    AvaProfile = ResampAvaPath
    # find split point by computing the distance to the line
    if Point:
        projPoint = findSplitPoint(AvaProfile, Point)
    else:
        projPoint = None

    return AvaProfile, projPoint


def findSplitPoint(AvaProfile, Points):
    """ Finds the closest point in Points to the AvaProfile and returns
    its projection on AvaProfile.
    """
    xcoor = AvaProfile['x']
    ycoor = AvaProfile['y']
    Dist = np.empty((0))
    IndSplit = np.empty((0))
    for i in range(len(Points['x'])):
        dist = np.sqrt((xcoor - Points['x'][i])**2 +
                       (ycoor - Points['y'][i])**2)
        indSplit = np.argmin(dist)
        IndSplit = np.append(IndSplit, indSplit)
        Dist = np.append(Dist, dist[indSplit])

    ind = np.argmin(Dist)
    indSplit = int(IndSplit[ind])
    projPoint = {}
    projPoint['x'] = AvaProfile['x'][indSplit]
    projPoint['y'] = AvaProfile['y'][indSplit]
    projPoint['z'] = AvaProfile['z'][indSplit]
    projPoint['s'] = AvaProfile['s'][indSplit]
    projPoint['indSplit'] = indSplit
    return projPoint


def checkProfile(AvaProfile, projSplitPoint=None):
    """ check that the avalanche profiles goes from top to bottom """
    if projSplitPoint:
        indSplit = projSplitPoint['indSplit']
    if AvaProfile['z'][-1] > AvaProfile['z'][0]:
        log.info('Profile reversed')
        AvaProfile['x'] = np.flip(AvaProfile['x'])
        AvaProfile['y'] = np.flip(AvaProfile['y'])
        AvaProfile['z'] = np.flip(AvaProfile['z'])
        try:
            L = AvaProfile['s'][-1]
            AvaProfile['s'] = L - np.flip(AvaProfile['s'])
        except KeyError:
            pass

        if projSplitPoint:
            indSplit = len(AvaProfile['x']) - indSplit - 1
            projSplitPoint['indSplit'] = indSplit
            AvaProfile['indSplit'] = indSplit
        else:
            projSplitPoint = None
            AvaProfile['indSplit'] = None

    return projSplitPoint, AvaProfile


def findAngleProfile(tmp, deltaInd):
    """
    Find the beta point: first point under the beta value given in
    prepareFind10Point. Make sure that the delta_ind next indexes are also
    under the beta value otherwise keep looking
    """
    noBetaFoundMessage = 'No Beta point found. Check your pathAB.shp and splitPoint.shp.'
    i = 0
    condition = True
    if np.size(tmp) == 0:
        raise IndexError(noBetaFoundMessage)
    while (i <= np.size(tmp) and condition):
        ind = tmp[0][i]
        for j in range(deltaInd):
            try:
                condition = condition and (tmp[0][i+j+1] == ind+j+1)
            except IndexError:
                raise IndexError(noBetaFoundMessage)
            if not condition:
                i = i + j + 1
                break
        if condition:
            idsAnglePoint = ind
            break
        condition = True
    return idsAnglePoint


def prepareAngleProfile(beta, AvaProfile):
    """
    Prepare inputs for findBetaPoint function: Read profile, compute Angle
    look for points for which the slope is under the given Beta value and
    that are located downstreem of the splitPoint
    """

    s = AvaProfile['s']
    z = AvaProfile['z']
    distance = s[1] - s[0]
    deltaInd = max(int(np.floor(30/distance)), 1)
    try:
        indSplit = AvaProfile['indSplit']
        CuSplit = s[indSplit]
    except KeyError:
        log.warning('No split Point given!')
        CuSplit = 0
    ds = np.abs(s - np.roll(s, 1))
    dz = np.roll(z, 1) - z
    ds[0] = 0.0
    dz[0] = 0.0
    angle = np.rad2deg(np.arctan2(dz, ds))
    # get all values where Angle < 10 but >0
    # get index of first occurance and go one back to get previous value
    # (i.e. last value above 10 deg)
    # tmp = x[(angle < 10.0) & (angle > 0.0) & (x > 450)]
    tmp = np.where((angle <= beta) & (s > CuSplit))
    return angle, tmp, deltaInd


def findCellsCrossedByLineBresenham(x0, y0, x1, y1, cs):
    """
    bresenham algorithmus - JT 2011
    Find all the cells of a raster (defined by its cellsize) that a line
    (defines by two points P0 and P1) crosses.
    input: x0, y0, x1, y1,cellsize
    output: array of x y coodinates of cells hit inbetween

    C IMPLEMENTIERUNG von http://de.wikipedia.org/wiki/Bresenham-Algorithmus
    void line(int x0, int y0, int x1, int y1)
     {
       int dx =  abs(x1-x0), sx = x0<x1 ? 1 : -1;
       int dy = -abs(y1-y0), sy = y0<y1 ? 1 : -1;
       int err = dx+dy, e2; /* error value e_xy */

       for(;;){  /* loop */
         setPixel(x0,y0);
         if (x0==x1 && y0==y1) break;
         e2 = 2*err;
         if (e2 > dy) { err += dy; x0 += sx; } /* e_xy+e_x > 0 */
         if (e2 < dx) { err += dx; y0 += sy; } /* e_xy+e_y < 0 */
       }
     }
    """
    # normalize Cellsize cs to 1
    x0 = round(x0/cs)
    x1 = round(x1/cs)
    y0 = round(y0/cs)
    y1 = round(y1/cs)

    dx = abs(x1-x0)
    dy = abs(y1-y0)
    sx = np.sign(x1-x0)  # step in x direction
    sy = np.sign(y1-y0)  # step in y direction
    err = dx-dy
    errprev = dx-dy

    z = []
    while True:
        z.append([x0*cs, y0*cs])
        if x0 == x1 and y0 == y1:  # if no step exists we are already there
            break
        e2 = 2*err
        if (e2 > -dy):
            err -= dy
            x0 += sx
            # if (err + errprev < -dy):
            #     z.append([x0*cs, (y0+sy)*cs])
            # elif (err + errprev < dx):
            #     z.append([x0*cs, y0*cs])
            # else:
            #     z.append([x0*cs, (y0+sy)*cs])
            #     z.append([(x0+sx)*cs, y0*cs])
        if (e2 < dx):
            err += dx
            y0 += sy
            # if (err + errprev < -dy):
            #     z.append([x0*cs, (y0+sy)*cs])
            # elif (err + errprev > dx):
            #     z.append([(x0+sx)*cs, y0*cs])
            # else:
            #     z.append([x0*cs, (y0+sy)*cs])
            #     z.append([(x0+sx)*cs, y0*cs])

    return z


def findCellsCrossedByLineBresenham2(x0, y0, x1, y1, cs):
    # normalize Cellsize cs to 1
    x0 = round(x0/cs)
    x1 = round(x1/cs)
    y0 = round(y0/cs)
    y1 = round(y1/cs)

    dx = abs(x1-x0)
    dy = abs(y1-y0)
    sx = np.sign(x1-x0)  # step in x direction
    sy = np.sign(y1-y0)  # step in y direction

    x = x0
    y = y0
    n = dx + dy
    err = dx - dy

    dx = 2 * dx
    dy = 2 * dy

    z = []
    while n > 0:
        z.append([x*cs, y*cs])
        if (err > 0):
            x += sx
            err -= dy
        elif (err < 0):
            y += sy
            err += dx
        else:  # If err == 0 the algorithm is on a corner
            z.append([x*cs, (y + sy)*cs])
            z.append([(x + sy)*cs, y*cs])
            x += sy
            y += sy
            err = err + dx - dy
            n = n - 1
        n = n - 1

    return z


def path2domain(xyPath, rasterTransfo):
    """
    path2domain
    Creates a domain (irregular raster) along a path, given the path polyline,
    a domain width and a raster cellsize
    Usage:
        [rasterTransfo] = path2domain(xyPath, rasterTransfo)
       Input:
           -xyPath:   Polyline Coordinates
           -rasterTransfo['w']:      Domain width
           -rasterTransfo['xllc']: xllc
           -rasterTransfo['yllc']: yllc
           -rasterTransfo['cellsize']: cellsize
       Output: xp, yp Arrays determining a path of width w along a polyline
            -rasterTransfo['DBXl']: x coord of the left boundary
            -rasterTransfo['DBXr']: x coord of the right boundary
            -rasterTransfo['DBYl']: y coord of the left boundary
            -rasterTransfo['DBYr']: y coord of the right boundary

    [Fischer2013] Fischer, Jan-Thomas. (2013).
    A novel approach to evaluate and compare computational snow avalanche
    simulation.
    Natural Hazards and Earth System Sciences.
    13. 1655-. 10.5194/nhess-13-1655-2013.
    Uwe Schlifkowitz/ BFW, June 2011
    """
    xllc = rasterTransfo['xllc']
    yllc = rasterTransfo['yllc']
    csz = rasterTransfo['cellsize']
    x = xyPath['x']
    y = xyPath['y']
    w = rasterTransfo['domainWidth']/2/csz
    # Shift grid origin to (0,0)
    x = x - xllc
    y = y - yllc
    # remove scaling due to cellsize
    x = x/csz
    y = y/csz

    # Difference between x- bzw. y-Coordinates of Polyline
    # first and last  Vertex: Difference between this and the next
    # other vertices: Difference between previous and next
    dx = np.array((x[1]-x[0]))
    dy = np.array((y[1]-y[0]))
    n = len(x)
    for i in range(2, n):
        dx = np.append(dx, (x[i]-x[i-2])/2.)
        dy = np.append(dy, (y[i]-y[i-2])/2.)

    dx = np.append(dx, x[-1]-x[-2])
    dy = np.append(dy, y[-1]-y[-2])

    # Direction of normal vector of difference,
    # a.k.a. bisecting line of angle
    d = np.arctan2(dy, dx) + math.pi/2

    # x- and y-Coordinates (left and right) of path edges,
    # total width w
    # x-KOO[left right]
    DBXl = np.array((x + w * np.cos(d)))
    DBXr = np.array((x + w * np.cos(d + math.pi)))
    # y-KOO[left right]
    DBYl = np.array((y + w * np.sin(d)))
    DBYr = np.array((y + w * np.sin(d + math.pi)))

    rasterTransfo['DBXl'] = DBXl
    rasterTransfo['DBXr'] = DBXr
    rasterTransfo['DBYl'] = DBYl
    rasterTransfo['DBYr'] = DBYr

    return rasterTransfo


def poly2maskSimple(ydep, xdep, ncols, nrows):
    """
    poly2maskSimple
    Create a mask from a polyline
    Usage:
        mask = poly2maskSimple(ydep, xdep, ncols, nrows)
       Input:
           ydep, xdep:      Polyline Coordinates
           ncols, nrows:    Raster size
       Output:
           mask:            Raster of the polyline mask

    """
    mask = np.zeros((nrows, ncols))
    xyframe = findCellsCrossedByLineBresenham(xdep[0], ydep[0], xdep[1],
                                              ydep[1], 1)
    xyframe = np.delete(xyframe, -1, 0)
    xyframe = np.transpose(xyframe)
    for i in range(1, len(xdep)-1):
        xyline = findCellsCrossedByLineBresenham(xdep[i], ydep[i], xdep[i+1],
                                                 ydep[i+1], 1)
        # last point is first point of the next line
        xyline = np.delete(xyline, -1, 0)
        xyline = np.transpose(xyline)
        xyframe = np.hstack((xyframe, xyline))

    xyline = findCellsCrossedByLineBresenham(xdep[-1], ydep[-1], xdep[0],
                                             ydep[0], 1)
    xyline = np.delete(xyline, -1, 0)
    xyline = np.transpose(xyline)
    xyframe = np.hstack((xyframe, xyline))
    for i in range(0, len(xyframe[0, :])):
        mask[xyframe[0, i], xyframe[1, i]] = 1

    # filling the inside of the polygon with ones
    i = xyframe[0]
    j = xyframe[1]
    mv, nv = np.meshgrid(np.linspace(0, nrows-1, nrows),
                         np.linspace(0, ncols-1, ncols))  # create index space
    # mask = inpolygon(mv, nv, i, j)
    # mask = np.transpose(mask)
    return mask


def inpolygon(X, Y, xv, yv):
    """
    inpolygon
    For a polygon defined by vertex points (xv, yv),
    returns a np array of size X with ones if the points (X, Y)
    are inside (or on the boundary) of the polygon;
    Otherwise, returns zeros.
    Usage:
        mask = inpolygon(X, Y, xv, yv)
       Input:
           X, Y:      Set of points to check
           xv, yv:    polygon vertex points
       Output:
           mask:      np array of zeros and ones

    Octave Implementation [IN, ON] = inpolygon (X, Y, xv, yv)
    """
    npol = len(xv)
    maxXv = np.max(xv)
    minXv = np.min(xv)
    maxYv = np.max(yv)
    minYv = np.min(yv)
    IN = np.zeros(np.shape(X))
    j = npol-1
    for i in range(npol-1):
        deltaxv = xv[j] - xv[i]
        deltayv = yv[j] - yv[i]
        # distance = [distance from (X,Y) to edge] * length(edge)
        distance = deltaxv*(Y-yv[i]) - (X-xv[i])*deltayv
        # is Y between the y-values of edge i,j
        # AND (X,Y) on the left of the edge ?
        for ii in range(minYv-1, maxYv+1, 1):
            for jj in range(minXv-1, maxXv+1, 1):
                if (((yv[i] <= Y[ii][jj] and Y[ii][jj] < yv[j]) or (yv[j] <= Y[ii][jj] and Y[ii][jj] < yv[i])) and (0 < distance[ii][jj]*deltayv)):
                    if IN[ii][jj] == 0:
                        IN[ii][jj] = 1
                    else:
                        IN[ii][jj] = 0
        j = i
    for i in range(npol-1):
        IN[yv[i]][xv[i]] = 1

    return IN


def inpolygon2(X, Y, xv, yv):
    """
    inpolygon
    For a polygon defined by vertex points (xv, yv),
    returns a np array of size X with ones if the points (X, Y)
    are inside (or on the boundary) of the polygon;
    Otherwise, returns zeros.
    Usage:
        mask = inpolygon(X, Y, xv, yv)
       Input:
           X, Y:      Set of points to check
           xv, yv:    polygon vertex points
       Output:
           mask:      np array of zeros and ones

    Octave Implementation [IN, ON] = inpolygon (X, Y, xv, yv)
    """
    npol = len(xv)
    maxXv = np.max(xv)
    minXv = np.min(xv)
    maxYv = np.max(yv)
    minYv = np.min(yv)
    IN = np.zeros(np.shape(X))
    for ii in range(minYv-1, maxYv+1, 1):
        for jj in range(minXv-1, maxXv+1, 1):
            inside = False
            x = X[ii][jj]
            y = Y[ii][jj]
            p1x = xv[npol-1]
            p1y = yv[npol-1]
            for i in range(npol-1):
                p2x = xv[i]
                p2y = yv[i]
                if y > min(p1y, p2y):
                    if y <= max(p1y, p2y):
                        if x <= max(p1x, p2x):
                            if p1y != p2y:
                                xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                            if p1x == p2x or x <= xinters:
                                inside = not inside
                p1x, p1y = p2x, p2y
            IN[ii][jj] = int(inside)

    for i in range(npol-1):
        IN[yv[i]][xv[i]] = 1

    return IN


def areaPoly(X, Y):
    ''' Gauss's area formula to calculate polygon area
    Inputs : - X coord of the vertices
             - Y coord of the vertices
    Output : Area of the polygon
    '''
    X = np.append(X, X[0])
    Y = np.append(Y, Y[0])
    sum = 0
    for i in range(np.size(X)-1):
        sum = sum + (X[i]*Y[i+1]-Y[i]*X[i+1])/2
    return sum
