"""Tests for module com1DFAtools"""
import numpy as np
import pytest

# Local imports
import avaframe.in2Trans.ascUtils as IOf
import avaframe.com1DFA.DFAfunctionsCython as DFAfunC
import avaframe.com1DFA.DFAtools as DFAtls


def test_normalizeC(capfd):
    '''test DFAfunctions tools
    norm, norm2, normalize, crossProd and scalProd'''
    x = np.array([1.])
    y = np.array([1.])
    z = np.array([1.])
    norme = DFAfunC.norm(x, y, z)
    norme2 = DFAfunC.norm2(x, y, z)
    xn, yn, zn = DFAfunC.normalize(x, y, z)
    print(xn, yn, zn)
    atol = 1e-10
    assert norme == np.sqrt(3.)
    assert norme2 == 3.
    assert np.sqrt(xn*xn + yn*yn + zn*zn) == pytest.approx(1., rel=atol)
    assert xn == 1/np.sqrt(3.)
    assert yn == 1/np.sqrt(3.)
    assert zn == 1/np.sqrt(3.)

    x = np.array([0.])
    y = np.array([0.])
    z = np.array([1e-18])
    xn, yn, zn = DFAfunC.normalize(x, y, z)
    assert np.sqrt(xn*xn + yn*yn + zn*zn) == pytest.approx(1, rel=atol)

    x = np.array([0.])
    y = np.array([0.])
    z = np.array([0.])
    xn, yn, zn = DFAfunC.normalize(x, y, z)
    assert np.sqrt(xn*xn + yn*yn + zn*zn) == pytest.approx(0, rel=atol)

    x = np.array([1.])
    y = np.array([2.])
    z = np.array([3.])
    xn, yn, zn = DFAfunC.normalize(x, y, z)
    assert np.sqrt(xn*xn + yn*yn + zn*zn) == pytest.approx(1., rel=atol)

    x = np.array([1.])
    y = np.array([0.])
    z = np.array([1.])
    xn, yn, zn = DFAfunC.normalize(x, y, z)
    assert np.sqrt(xn*xn + yn*yn + zn*zn) == pytest.approx(1, rel=atol)
    assert xn == pytest.approx(1/np.sqrt(2.), rel=atol)
    assert yn == pytest.approx(0, rel=atol)
    assert zn == pytest.approx(1/np.sqrt(2.), rel=atol)

    x = np.array([1.])
    y = np.array([2.])
    z = np.array([3.])
    x1 = np.array([4.])
    y1 = np.array([5.])
    z1 = np.array([6.])
    xn, yn, zn = DFAfunC.crossProd(x, y, z, x1, y1, z1)
    assert xn == -3
    assert yn == 6
    assert zn == -3

    x = np.array([1.])
    y = np.array([2.])
    z = np.array([3.])
    x1 = np.array([4.])
    y1 = np.array([5.])
    z1 = np.array([6.])
    scal = DFAfunC.scalProd(x, y, z, x1, y1, z1)
    assert scal == 32


def test_getWeightsC(capfd):
    '''getWeights getScalar and getVector'''
    ncols = 4
    nrows = 3
    X = np.array([0., 1, 2.5, 4., 4., 4.9])
    Y = np.array([0., 0., 2.5, 2.5, 3., 4.9])
    F00 = np.array([[1., 1., 0., 0., 0., 0.],
                    [1./4, 1./4, 1./4, 1./4, 1./4, 1./4],
                    [1., 0.8, 1./4, 0.09999999999999998, 0.07999999999999999, 0.0003999999999999963]])
    F10 = np.array([[0., 0., 0., 0., 0., 0.],
                    [1./4, 1./4, 1./4, 1./4, 1./4, 1./4],
                    [0., 0.2, 1./4, 0.4, 0.32, 0.01959999999999991]])
    F01 = np.array([[0., 0., 0., 0., 0., 0.],
                    [1./4, 1./4, 1./4, 1./4, 1./4, 1./4],
                    [0., 0., 1./4, 0.09999999999999998, 0.11999999999999997, 0.01959999999999991]])
    F11 = np.array([[0., 0., 1., 1., 1., 1.],
                    [1./4, 1./4, 1./4, 1./4, 1./4, 1./4],
                    [0., 0., 1./4, 0.4, 0.48, 0.9604000000000001]])
    csz = 5.
    atol = 1e-10
    # option 0: nearest, 1, unifom, 2 bilinear
    for interpOption in range(3):
        FF00 = F00[interpOption]
        FF10 = F10[interpOption]
        FF01 = F01[interpOption]
        FF11 = F11[interpOption]
        for x, y, ff00, ff10, ff01, ff11 in zip(X, Y, FF00, FF10, FF01, FF11):
            Lx0, Ly0, iCell, f00, f10, f01, f11 = DFAfunC.getCellAndWeights(x, y, ncols, nrows, csz, interpOption)
            print(Lx0, Ly0)
            print(f00, f10, f01, f11)
            assert Lx0 == 0.
            assert Ly0 == 0.
            assert iCell == 0.
            assert ff00 == pytest.approx(f00, rel=atol)
            assert ff10 == pytest.approx(f10, rel=atol)
            assert ff01 == pytest.approx(f01, rel=atol)
            assert ff11 == pytest.approx(f11, rel=atol)

    # same as before but shift 2 in x dir and 1 in y dir
    X = X + 2*csz
    Y = Y + csz
    for interpOption in range(3):
        FF00 = F00[interpOption]
        FF10 = F10[interpOption]
        FF01 = F01[interpOption]
        FF11 = F11[interpOption]
        for x, y, ff00, ff10, ff01, ff11 in zip(X, Y, FF00, FF10, FF01, FF11):
            Lx0, Ly0, iCell, f00, f10, f01, f11 = DFAfunC.getCellAndWeights(x, y, ncols, nrows, csz, interpOption)
            print(Lx0, Ly0, iCell)
            print(f00, f10, f01, f11)
            assert Lx0 == 2.
            assert Ly0 == 1.
            assert iCell == 6.
            assert ff00 == pytest.approx(f00, rel=atol)
            assert ff10 == pytest.approx(f10, rel=atol)
            assert ff01 == pytest.approx(f01, rel=atol)
            assert ff11 == pytest.approx(f11, rel=atol)


def test_getNormalMesh(capfd):
    '''projectOnRaster'''
    a = 2
    b = 1
    cellsize = 1
    m = 10
    n = 15
    x = np.linspace(0, m-1, m)
    y = np.linspace(0, n-1, n)
    X, Y = np.meshgrid(x, y)
    Z = a * X + b * Y
    header = IOf.cASCheader()
    header.ncols = m
    header.nrows = n
    header.cellsize = cellsize
    dem = {}
    dem['header'] = header
    Z1 = a * X * X + b * Y * Y
    for num in [4, 6, 8]:
        dem['rasterData'] = Z
        Nx, Ny, Nz = DFAtls.getNormalMesh(dem, num)
        Nx, Ny, Nz = DFAtls.normalize(Nx, Ny, Nz)
        print(Nx)
        print((-a*np.ones(np.shape(Y)) / np.sqrt(1 + a*a + b*b))[1:n-1, 1:m-1])
        print(Ny)
        print((-b*np.ones(np.shape(Y)) / np.sqrt(1 + a*a + b*b))[1:n-1, 1:m-1])
        print(Nz)
        print((np.ones(np.shape(Y)) / np.sqrt(1 + a*a + b*b))[1:n-1, 1:m-1])

        atol = 1e-10
        TestNX = np.allclose(Nx[1:n-1, 1:m-1], (-a*np.ones(np.shape(Y)) /
                                                np.sqrt(1 + a*a + b*b))[1:n-1, 1:m-1], atol=atol)
        assert TestNX
        TestNY = np.allclose(Ny[1:n-1, 1:m-1], (-b*np.ones(np.shape(Y)) /
                                                np.sqrt(1 + a*a + b*b))[1:n-1, 1:m-1], atol=atol)
        assert TestNY
        TestNZ = np.allclose(Nz[1:n-1, 1:m-1], (np.ones(np.shape(Y)) /
                                                np.sqrt(1 + a*a + b*b))[1:n-1, 1:m-1], atol=atol)
        assert TestNZ

        dem['rasterData'] = Z1
        Nx, Ny, Nz = DFAtls.getNormalMesh(dem, num)
        Nx, Ny, Nz = DFAtls.normalize(Nx, Ny, Nz)

        print(Nx)
        print((-2*a*X / np.sqrt(1 + 4*a*a*X*X + 4*b*b*Y*Y))[1:n-1, 1:m-1])
        print(Ny)
        print((-2*b*Y / np.sqrt(1 + 4*a*a*X*X + 4*b*b*Y*Y))[1:n-1, 1:m-1])
        print(Nz)
        print((1 / np.sqrt(1 + 4*a*a*X*X + 4*b*b*Y*Y))[1:n-1, 1:m-1])
        atol = 1e-10
        TestNX = np.allclose(Nx[1:n-1, 1:m-1], (-2*a*X / np.sqrt(1 + 4*a *
                                                                 a*X*X + 4*b*b*Y*Y))[1:n-1, 1:m-1], atol=atol)
        assert TestNX
        TestNY = np.allclose(Ny[1:n-1, 1:m-1], (-2*b*Y / np.sqrt(1 + 4*a *
                                                                 a*X*X + 4*b*b*Y*Y))[1:n-1, 1:m-1], atol=atol)
        assert TestNY
        TestNZ = np.allclose(Nz[1:n-1, 1:m-1], (1 / np.sqrt(1 + 4*a*a *
                                                            X*X + 4*b*b*Y*Y))[1:n-1, 1:m-1], atol=atol)
        assert TestNZ


def test_getAreaMesh(capfd):
    '''projectOnRaster'''
    a = 0.1
    b = 0.2
    csz = 1
    m = 15
    n = 10
    x = np.linspace(0, m-1, m)
    y = np.linspace(0, n-1, n)
    X, Y = np.meshgrid(x, y)
    Z = a * X + b * Y
    Z1 = a * X * X + b * Y * Y
    header = IOf.cASCheader()
    header.ncols = m
    header.nrows = n
    header.cellsize = csz
    dem = {}
    dem['header'] = header
    dem['rasterData'] = Z
    Nx, Ny, Nz = DFAtls.getNormalMesh(dem, 4)
    Nx, Ny, Nz = DFAtls.normalize(Nx, Ny, Nz)
    Area = DFAtls.getAreaMesh(Nx, Ny, Nz, csz, 4)
    print(np.sqrt((1+a*a+b*b)))
    print(Area)
    atol = 1e-10
    TestArea = np.allclose(Area[1:n-1, 1:m-1], np.sqrt((1+a*a+b*b)) *
                           np.ones(np.shape(Y[1:n-1, 1:m-1])), atol=atol)
    assert TestArea


def test_getNeighborsC(capfd):
    """ Test the grid search/particle location method"""
    header = IOf.cASCheader()
    header.ncols = 5
    header.nrows = 6
    header.cellsize = 1
    dem = {}
    dem['header'] = header
    dem['headerNeighbourGrid'] = header
    particles = {}
    particles['Npart'] = 18
    particles['x'] = np.array([1.6, 0.4, 1, 2, 1, 2, 0, 1, 0, 2, 0, 2, 1, 2, 3, 3, 4, 0])
    particles['y'] = np.array([2.6, 1.4, 0, 1, 3, 3, 2, 1, 0, 0, 3, 2, 2, 1, 1, 4, 5, 5])
    particles['z'] = np.array([0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.])
    particles['m'] = particles['z']
    atol = 1e-10
    indPCell = np.array([0.,  # always an extra zero at the begining
                         1,  # found 1 particle
                         2,  # found 1 particle
                         3,  # found 1 particle
                         3,  # nothing happens
                         3,  # nothing happens
                         4,  # found 1 particle
                         5,  # found 1 particle
                         7,   # found 2 particles
                         8,  # found 1 particle
                         8,  # nothing happens
                         9,  # found 1 particle
                         10,  # found 1 particle
                         11,   # found 1 particles
                         11, 11,  # nothing happens
                         12,  # found 1 particle
                         13,  # found 1 particle
                         15,  # found 2 particle
                         15, 15, 15, 15, 15,  # nothing happens
                         16,  # found 1 particle
                         16,  # nothing happens
                         17,  # found 1 particle
                         17, 17, 17,  # nothing happens
                         18])  # found 1 particle
    pInC = np.array([8,
                     2,
                     9,
                     1,
                     7,
                     13, 3,
                     14,
                     6,
                     12,
                     11,
                     10,
                     4,
                     5, 0,
                     15,
                     17,
                     16])

    particles = DFAfunC.getNeighborsC(particles, dem)
    print(particles['inCellDEM'])
    print(particles['indPartInCell'])
    print(particles['partInCell'])
    assert np.allclose(particles['indPartInCell'], indPCell, atol=atol)
    assert np.allclose(particles['partInCell'], pInC, atol=atol)
