"""Tests for module DFAtools"""
import numpy as np
import pytest

# Local imports
import avaframe.com1DFA.DFAtools as DFAtls


def test_normalize(capfd):
    '''test DFAfunctions tools
    norm, norm2, normalize, crossProd and scalProd'''
    x = np.array([1.])
    y = np.array([1.])
    z = np.array([1.])
    norme = DFAtls.norm(x, y, z)
    norme2 = DFAtls.norm2(x, y, z)
    xn, yn, zn = DFAtls.normalize(x, y, z)
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
    xn, yn, zn = DFAtls.normalize(x, y, z)
    assert np.sqrt(xn*xn + yn*yn + zn*zn) == pytest.approx(1, rel=atol)

    x = np.array([0.])
    y = np.array([0.])
    z = np.array([0.])
    xn, yn, zn = DFAtls.normalize(x, y, z)
    assert np.sqrt(xn*xn + yn*yn + zn*zn) == pytest.approx(0, rel=atol)

    x = np.array([1.])
    y = np.array([2.])
    z = np.array([3.])
    xn, yn, zn = DFAtls.normalize(x, y, z)
    assert np.sqrt(xn*xn + yn*yn + zn*zn) == pytest.approx(1., rel=atol)

    x = np.array([1.])
    y = np.array([0.])
    z = np.array([1.])
    xn, yn, zn = DFAtls.normalize(x, y, z)
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
    xn, yn, zn = DFAtls.crossProd(x, y, z, x1, y1, z1)
    assert xn == -3
    assert yn == 6
    assert zn == -3

    x = np.array([1.])
    y = np.array([2.])
    z = np.array([3.])
    x1 = np.array([4.])
    y1 = np.array([5.])
    z1 = np.array([6.])
    scal = DFAtls.scalProd(x, y, z, x1, y1, z1)
    assert scal == 32


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
    header = {}
    header['ncols'] = m
    header['nrows'] = n
    header['cellsize'] = cellsize
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
    header = {}
    header['ncols'] = m
    header['nrows'] = n
    header['cellsize'] = csz
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


def test_removePart(capfd):
    particles = {}
    particles['Npart'] = 10
    particles['m'] = np.linspace(0, 9, 10)
    particles['x'] = np.linspace(0, 9, 10)
    particles['ux'] = np.linspace(0, 9, 10)
    particles['mTot'] = np.sum(particles['m'])
    mask = np.array([True, True, False, True, True, True, False, False, True, True])
    nRemove = 3
    particles = DFAtls.removePart(particles, mask, nRemove)

    res = np.array([0, 1, 3, 4, 5, 8, 9])
    atol = 1e-10
    assert particles['Npart'] == 7
    assert np.allclose(particles['m'], res, atol=atol)
    assert np.allclose(particles['x'], res, atol=atol)
    assert np.allclose(particles['ux'], res, atol=atol)
    assert particles['mTot'] == np.sum(res)


def test_splitPart(capfd):
    particles = {}
    particles['Npart'] = 10
    particles['massPerPart'] = 1
    particles['m'] = np.array([1, 2, 1, 3.6, 1, 1, 5, 1, 1, 1])
    particles['x'] = np.linspace(0, 9, 10)
    particles['ux'] = np.linspace(0, 9, 10)
    particles['mTot'] = np.sum(particles['m'])
    particles = DFAtls.splitPart(particles)
    print(particles)
    massNew = np.array([1, 1, 1, 0.9, 1, 1, 1, 1, 1, 1, 1, 0.9, 0.9, 0.9, 1, 1, 1, 1])
    res = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 3, 3, 3, 6, 6, 6, 6])
    print(particles['m'])
    print(massNew)
    atol = 1e-10
    assert particles['Npart'] == 18
    assert np.allclose(particles['m'], massNew, atol=atol)
    assert np.allclose(particles['x'], res, atol=atol)
    assert np.allclose(particles['ux'], res, atol=atol)
    assert particles['mTot'] == np.sum(massNew)


def test_mergeParticleDict(capfd):

    particles1 = {}
    particles1['Npart'] = 5
    particles1['m'] = np.linspace(0, 4, 5)
    particles1['x'] = np.linspace(0, 4, 5)
    particles1['ux'] = np.linspace(0, 4, 5)
    particles1['mTot'] = np.sum(particles1['m'])

    particles2 = {}
    particles2['Npart'] = 4
    particles2['m'] = np.linspace(5, 8, 4)
    particles2['x'] = np.linspace(5, 8, 4)
    particles2['ux'] = np.linspace(5, 8, 4)
    particles2['mTot'] = np.sum(particles1['m'])

    particles = DFAtls.mergeParticleDict(particles1, particles2)
    res = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8])
    atol = 1e-10
    assert particles['Npart'] == 9
    assert np.allclose(particles['m'], res, atol=atol)
    assert np.allclose(particles['x'], res, atol=atol)
    assert np.allclose(particles['ux'], res, atol=atol)
    assert particles['mTot'] == np.sum(res)
