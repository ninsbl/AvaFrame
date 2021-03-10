"""
    Basic tools for getting grid normals, area and working with vectors.
"""

# Load modules
import logging
import numpy as np

# Local imports
import avaframe.in3Utils.geoTrans as geoTrans


# create local logger
# change log level in calling module to DEBUG to see log messages
log = logging.getLogger(__name__)


def getNormalArray(x, y, Nx, Ny, Nz, csz):
    """ Interpolate vector field from grid to unstructures points

        Originaly created to get the normal vector at location (x,y) given the
        normal vector field on the grid. Grid has its origin in (0,0).
        Can be used to interpolate any vector field.
        Interpolation using a bilinear interpolation

        Parameters
        ----------
            x: numpy array
                location in the x location of desiered interpolation
            y: numpy array
                location in the y location of desiered interpolation
            Nx: 2D numpy array
                x component of the vector field at the grid nodes
            Ny: 2D numpy array
                y component of the vector field at the grid nodes
            Nz: 2D numpy array
                z component of the vector field at the grid nodes
            csz: float
                cellsize of the grid

        Returns
        -------
            nx: numpy array
                x component of the interpolated vector field at position (x, y)
            ny: numpy array
                y component of the interpolated vector field at position (x, y)
            nz: numpy array
                z component of the interpolated vector field at position (x, y)
    """
    nrow, ncol = np.shape(Nx)
    # by default bilinear interpolation of the Nx, Ny, Nz of the grid
    nx, _ = geoTrans.projectOnGrid(x, y, Nx, csz=csz)
    ny, _ = geoTrans.projectOnGrid(x, y, Ny, csz=csz)
    nz, _ = geoTrans.projectOnGrid(x, y, Nz, csz=csz)
    return nx, ny, nz


def getNormalMesh(z, csz, num):
    """ Compute normal to surface at grid points

        Get the normal vectors to the surface defined by a DEM.
        Either by adding the normal vectors of the adjacent triangles for each
        points (using 4, 6 or 8 adjacent triangles). Or use the next point in
        x direction and the next in y direction to define two vectors and then
        compute the cross product to get the normal vector

        Parameters
        ----------
            z: 2D numpy array
                elevation at grid points
            csz: float
                cellsize of the grid
            num: int
                chose between 4, 6 or 8 (using then 4, 6 or 8 triangles) or
                       1 to use the simple cross product method (with the diagonals)

        Returns
        -------
            Nx: 2D numpy array
                x component of the normal vector field on grid points
            Ny: 2D numpy array
                y component of the normal vector field on grid points
            Nz: 2D numpy array
                z component of the normal vector field on grid points
    """
    n, m = np.shape(z)
    Nx = np.ones((n, m))
    Ny = np.ones((n, m))
    Nz = np.ones((n, m))
    # first and last row, first and last column are inacurate
    if num == 4:
        # filling the inside of the matrix
        # normal calculation with 4 triangles
        # (Zl - Zr) / csz
        Nx[1:n-1, 1:m-1] = (z[1:n-1, 0:m-2] - z[1:n-1, 2:m]) / csz
        # (Zd - Zu) * csz
        Ny[1:n-1, 1:m-1] = (z[0:n-2, 1:m-1] - z[2:n, 1:m-1]) / csz
        Nz = 2 * Nz
        # filling the first col of the matrix
        # -2*(Zr - Zp) / csz
        Nx[1:n-1, 0] = - 2*(z[1:n-1, 1] - z[1:n-1, 0]) / csz
        # (Zd - Zu) / csz
        Ny[1:n-1, 0] = (z[0:n-2, 0] - z[2:n, 0]) / csz
        # filling the last col of the matrix
        # 2*(Zl - Zp) / csz
        Nx[1:n-1, m-1] = 2*(z[1:n-1, m-2] - z[1:n-1, m-1]) / csz
        # (Zd - Zu) / csz
        Ny[1:n-1, m-1] = (z[0:n-2, m-1] - z[2:n, m-1]) / csz
        # filling the first row of the matrix
        # (Zl - Zr) / csz
        Nx[0, 1:m-1] = (z[0, 0:m-2] - z[0, 2:m]) / csz
        # -2*(Zu - Zp) / csz
        Ny[0, 1:m-1] = - 2*(z[1, 1:m-1] - z[0, 1:m-1]) / csz
        # filling the last row of the matrix
        # (Zl - Zr) / csz
        Nx[n-1, 1:m-1] = (z[n-1, 0:m-2] - z[n-1, 2:m]) / csz
        # 2*(Zd - Zp) / csz
        Ny[n-1, 1:m-1] = 2*(z[n-2, 1:m-1] - z[n-1, 1:m-1]) / csz
        # filling the corners of the matrix
        Nx[0, 0] = -(z[0, 1] - z[0, 0]) / csz
        Ny[0, 0] = -(z[1, 0] - z[0, 0]) / csz
        Nz[0, 0] = 1
        Nx[n-1, 0] = -(z[n-1, 1] - z[n-1, 0]) / csz
        Ny[n-1, 0] = (z[n-2, 0] - z[n-1, 0]) / csz
        Nz[n-1, 0] = 1
        Nx[0, m-1] = (z[0, m-2] - z[0, m-1]) / csz
        Ny[0, m-1] = -(z[1, m-1] - z[0, m-1]) / csz
        Nz[0, m-1] = 1
        Nx[n-1, m-1] = (z[n-1, m-2] - z[n-1, m-1]) / csz
        Ny[n-1, m-1] = (z[n-2, m-1] - z[n-1, m-1]) / csz
        Nz[n-1, m-1] = 1

    if num == 6:
        # filling the inside of the matrix
        # normal calculation with 6 triangles
        # (2*(Zl - Zr) - Zur + Zdl + Zu - Zd) / csz
        Nx[1:n-1, 1:m-1] = (2 * (z[1:n-1, 0:m-2] - z[1:n-1, 2:m])
                            - z[2:n, 2:m] + z[0:n-2, 0:m-2]
                            + z[2:n, 1:m-1] - z[0:n-2, 1:m-1]) / csz
        # (2*(Zd - Zu) - Zur + Zdl - Zl + Zr) / csz
        Ny[1:n-1, 1:m-1] = (2 * (z[0:n-2, 1:m-1] - z[2:n, 1:m-1])
                            - z[2:n, 2:m] + z[0:n-2, 0:m-2]
                            - z[1:n-1, 0:m-2] + z[1:n-1, 2:m]) / csz
        Nz = 6 * Nz
        # filling the first col of the matrix
        # (- 2*(Zr - Zp) + Zu - Zur ) / csz
        Nx[1:n-1, 0] = (- 2*(z[1:n-1, 1] - z[1:n-1, 0]) + z[2:n, 0] - z[2:n, 1]) / csz
        # (Zd - Zu + Zr - Zur) / csz
        Ny[1:n-1, 0] = (z[0:n-2, 0] - z[2:n, 0] + z[1:n-1, 1] - z[2:n, 1]) / csz
        Nz[1:n-1, 0] = 3
        # filling the last col of the matrix
        # (2*(Zl - Zp) + Zdl - Zd) / csz
        Nx[1:n-1, m-1] = (2*(z[1:n-1, m-2] - z[1:n-1, m-1]) + z[0:n-2, m-2] - z[0:n-2, m-1]) / csz
        # (Zd - Zu + Zdl - Zl) / csz
        Ny[1:n-1, m-1] = (z[0:n-2, m-1] - z[2:n, m-1] + z[0:n-2, m-2] - z[1:n-1, m-2]) / csz
        Nz[1:n-1, m-1] = 3
        # filling the first row of the matrix
        # (Zl - Zr + Zu - Zur) / csz
        Nx[0, 1:m-1] = (z[0, 0:m-2] - z[0, 2:m] + z[1, 1:m-1] - z[1, 2:m]) / csz
        # (-2*(Zu - Zp) + Zr - Zur) / csz
        Ny[0, 1:m-1] = (- 2*(z[1, 1:m-1] - z[0, 1:m-1]) + z[0, 2:m] - z[1, 2:m]) / csz
        Nz[0, 1:m-1] = 3
        # filling the last row of the matrix
        # (Zl - Zr + Zdl - Zd) / csz
        Nx[n-1, 1:m-1] = (z[n-1, 0:m-2] - z[n-1, 2:m] + z[n-2, 0:m-2] - z[n-2, 1:m-1]) / csz
        # (2*(Zd - Zp) + Zdl - Zl) / csz
        Ny[n-1, 1:m-1] = (2*(z[n-2, 1:m-1] - z[n-1, 1:m-1]) + z[n-2, 0:m-2] - z[n-1, 0:m-2]) / csz
        Nz[n-1, 1:m-1] = 3
        # filling the corners of the matrix
        Nx[0, 0] = (z[1, 0] - z[1, 1] - (z[0, 1] - z[0, 0])) / csz
        Ny[0, 0] = (z[0, 1] - z[1, 1] - (z[1, 0] - z[0, 0])) / csz
        Nz[0, 0] = 2
        Nx[n-1, 0] = -(z[n-1, 1] - z[n-1, 0]) / csz
        Ny[n-1, 0] = (z[n-2, 0] - z[n-1, 0]) / csz
        Nz[n-1, 0] = 1
        Nx[0, m-1] = (z[0, m-2] - z[0, m-1]) / csz
        Ny[0, m-1] = -(z[1, m-1] - z[0, m-1]) / csz
        Nz[0, m-1] = 1
        Nx[n-1, m-1] = (z[n-1, m-2] - z[n-1, m-1] + z[n-2, m-2] - z[n-2, m-1]) / csz
        Ny[n-1, m-1] = (z[n-2, m-1] - z[n-1, m-1] + z[n-2, m-2] - z[n-1, m-2]) / csz
        Nz[n-1, m-1] = 2

    if num == 8:
        # filling the inside of the matrix
        # normal calculation with 8 triangles
        # (2*(Zl - Zr) + Zul - Zur + Zdl - Zdr) / csz
        Nx[1:n-1, 1:m-1] = (2 * (z[1:n-1, 0:m-2] - z[1:n-1, 2:m])
                            + z[2:n, 0:m-2] - z[2:n, 2:m]
                            + z[0:n-2, 0:m-2] - z[0:n-2, 2:m]) / csz
        # (2*(Zd - Zu) - Zul - Zur + Zdl + Zdr) / csz
        Ny[1:n-1, 1:m-1] = (2 * (z[0:n-2, 1:m-1] - z[2:n, 1:m-1])
                            - z[2:n, 0:m-2] - z[2:n, 2:m]
                            + z[0:n-2, 0:m-2] + z[0:n-2, 2:m]) / csz
        Nz = 8 * Nz
        # filling the first col of the matrix
        # (- 2*(Zr - Zp) + Zu - Zur + Zd - Zdr) / csz
        Nx[1:n-1, 0] = (- 2*(z[1:n-1, 1] - z[1:n-1, 0]) + z[2:n, 0] - z[2:n, 1] + z[0:n-2, 0] - z[0:n-2, 1]) / csz
        # (Zd - Zu + Zdr - Zur) / csz
        Ny[1:n-1, 0] = (z[0:n-2, 0] - z[2:n, 0] + z[0:n-2, 1] - z[2:n, 1]) / csz
        Nz[1:n-1, 0] = 4
        # filling the last col of the matrix
        # (2*(Zl - Zp) + Zdl - Zd + Zul - Zu) / csz
        Nx[1:n-1, m-1] = (2*(z[1:n-1, m-2] - z[1:n-1, m-1]) + z[0:n-2, m-2] - z[0:n-2, m-1] + z[2:n, m-2] - z[2:n, m-1]) / csz
        # (Zd - Zu + Zdl - Zul) / csz
        Ny[1:n-1, m-1] = (z[0:n-2, m-1] - z[2:n, m-1] + z[0:n-2, m-2] - z[2:n, m-2]) / csz
        Nz[1:n-1, m-1] = 4
        # filling the first row of the matrix
        # (Zl - Zr + Zul - Zur) / csz
        Nx[0, 1:m-1] = (z[0, 0:m-2] - z[0, 2:m] + z[1, 0:m-2] - z[1, 2:m]) / csz
        # (-2*(Zu - Zp) + Zr - Zur + Zl - Zul) / csz
        Ny[0, 1:m-1] = (- 2*(z[1, 1:m-1] - z[0, 1:m-1]) + z[0, 2:m] - z[1, 2:m] + z[0, 0:m-2] - z[1, 0:m-2]) / csz
        Nz[0, 1:m-1] = 4
        # filling the last row of the matrix
        # (Zl - Zr + Zdl - Zdr) / csz
        Nx[n-1, 1:m-1] = (z[n-1, 0:m-2] - z[n-1, 2:m] + z[n-2, 0:m-2] - z[n-2, 2:m]) / csz
        # (2*(Zd - Zp) + Zdl - Zl + Zdr - Zr) / csz
        Ny[n-1, 1:m-1] = (2*(z[n-2, 1:m-1] - z[n-1, 1:m-1]) + z[n-2, 0:m-2] - z[n-1, 0:m-2] + z[n-2, 2:m] - z[n-1, 2:m]) / csz
        Nz[n-1, 1:m-1] = 4
        # filling the corners of the matrix
        Nx[0, 0] = (z[1, 0] - z[1, 1] - (z[0, 1] - z[0, 0])) / csz
        Ny[0, 0] = (z[0, 1] - z[1, 1] - (z[1, 0] - z[0, 0])) / csz
        Nz[0, 0] = 2
        Nx[n-1, 0] = (-(z[n-1, 1] - z[n-1, 0]) + z[n-2, 0] - z[n-2, 1]) / csz
        Ny[n-1, 0] = (z[n-2, 1] - z[n-1, 1] + z[n-2, 0] - z[n-1, 0]) / csz
        Nz[n-1, 0] = 2
        Nx[0, m-1] = (z[1, m-2] - z[1, m-1] + z[0, m-2] - z[0, m-1]) / csz
        Ny[0, m-1] = (-(z[1, m-1] - z[0, m-1]) + z[0, m-2] - z[1, m-2]) / csz
        Nz[0, m-1] = 2
        Nx[n-1, m-1] = (z[n-1, m-2] - z[n-1, m-1] + z[n-2, m-2] - z[n-2, m-1]) / csz
        Ny[n-1, m-1] = (z[n-2, m-1] - z[n-1, m-1] + z[n-2, m-2] - z[n-1, m-2]) / csz
        Nz[n-1, m-1] = 2

    if num == 1:
        # using the simple cross product
        z1 = np.append(z, z[:, -2].reshape(n, 1), axis=1)
        n1, m1 = np.shape(z1)
        z2 = np.append(z1, z1[-2, :].reshape(1, m1), axis=0)
        n2, m2 = np.shape(z2)

        Nx = - ((z2[0:n2-1, 1:m2] - z2[1:n2, 0:m2-1]) +
                (z2[1:n2, 1:m2] - z2[0:n2-1, 0:m2-1])) * csz
        Ny = - ((z2[1:n2, 1:m2] - z2[0:n2-1, 0:m2-1]) -
                (z2[0:n2-1, 1:m2] - z2[1:n2, 0:m2-1])) * csz
        Nz = 2 * Nz * csz * csz

        # Nx = - (z2[0:n2-1, 1:m2] - z2[0:n2-1, 0:m2-1]) / csz
        # Ny = - (z2[1:n2, 0:m2-1] - z2[0:n2-1, 0:m2-1]) / csz
        Ny[n-1, 0:m-1] = -Ny[n-1, 0:m-1]
        Nx[0:n-1, m-1] = -Nx[0:n-1, m-1]
        Ny[n-1, m-1] = -Ny[n-1, m-1]
        Nx[n-1, m-1] = -Nx[n-1, m-1]

    return 0.5*Nx, 0.5*Ny, 0.5*Nz


def getAreaMesh(Nx, Ny, Nz, csz, num):
    """ Get area of grid cells.

        Parameters
        ----------
            Nx: 2D numpy array
                x component of the normal vector field on grid points
            Ny: 2D numpy array
                y component of the normal vector field on grid points
            Nz: 2D numpy array
                z component of the normal vector field on grid points
            csz: float
                cellsize of the grid

        Returns
        -------
            A: 2D numpy array
                Area of grid cells
    """
    # see documentation and issue 202
    if num == 1:
        A = norm(Nx, Ny, Nz)
    else:
        _, _, NzNormed = normalize(Nx, Ny, Nz)
        A = csz * csz / NzNormed
    # limit maximum area (for very steeps cells)
    A = np.where(A > 3*csz*csz, 3*csz*csz, A)
    return A


def norm(x, y, z):
    """ Compute the Euclidean norm of the vector (x, y, z).

    (x, y, z) can be numpy arrays.

    Parameters
    ----------
        x: numpy array
            x component of the vector
        y: numpy array
            y component of the vector
        z: numpy array
            z component of the vector

    Returns
    -------
        norme: numpy array
            norm of the vector
    """
    norme = np.sqrt(x*x + y*y + z*z)
    return norme


def norm2(x, y, z):
    """ Compute the square of the Euclidean norm of the vector (x, y, z).

    (x, y, z) can be numpy arrays.

    Parameters
    ----------
        x: numpy array
            x component of the vector
        y: numpy array
            y component of the vector
        z: numpy array
            z component of the vector

    Returns
    -------
        norme2: numpy array
            square of the norm of the vector
    """
    norme2 = (x*x + y*y + z*z)
    return norme2


def normalize(x, y, z):
    """ Normalize vector (x, y, z) for the Euclidean norm.

    (x, y, z) can be np arrays.

    Parameters
    ----------
        x: numpy array
            x component of the vector
        y: numpy array
            y component of the vector
        z: numpy array
            z component of the vector

    Returns
    -------
        xn: numpy array
            x component of the normalized vector
        yn: numpy array
            y component of the normalized vector
        zn: numpy array
            z component of the normalized vector
    """
    # TODO : avoid error message when input vector is zero and make sure
    # to return zero
    norme = norm(x, y, z)
    xn = x / norme
    xn = np.where(np.isnan(xn), x, xn)
    xn = np.where(np.isnan(x), x, xn)
    yn = y / norme
    yn = np.where(np.isnan(yn), y, yn)
    yn = np.where(np.isnan(y), y, yn)
    zn = z / norme
    zn = np.where(np.isnan(zn), z, zn)
    zn = np.where(np.isnan(z), z, zn)

    return xn, yn, zn


def croosProd(ux, uy, uz, vx, vy, vz):
    """ Compute cross product of vector u = (ux, uy, uz) and v = (vx, vy, vz).
    """
    wx = uy*vz - uz*vy
    wy = uz*vx - ux*vz
    wz = ux*vy - uy*vx

    return wx, wy, wz


def scalProd(ux, uy, uz, vx, vy, vz):
    """ Compute scalar product of vector u = (ux, uy, uz) and v = (vx, vy, vz).
    """
    scal = ux*vx + uy*vy + uz*vz

    return scal
