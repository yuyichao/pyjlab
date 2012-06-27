# coding=utf-8

# Copyright 2012 Yu Yichao, Rudy H Tanin
# yyc1992@gmail.com
# rudyht@gmail.com
#
# This file is part of Jlab.
#
# Jlab is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Jlab is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Jlab.  If not, see <http://www.gnu.org/licenses/>.

from .general import *

from scipy.optimize import curve_fit, leastsq

def _init_l_w_sig(x, sig0):
    l = len(x)
    a = ones(l)
    if sig0 == None:
        return (l, a, a.copy(), None)
    sig = a * sig0
    return (l, sig, 1 / sig**2, sig0)

def _init_l_w(x, sig0):
    l = len(x)
    a = ones(l)
    if sig0 == None:
        return (l, a)
    return (l, (a / sig0)**2)

def fitlin(x, y, sig=None):
    x = array(x)
    y = array(y)

    l, w = _init_l_w(x, sig)

    wx = w * x
    wy = w * y

    wxs = sum(wx)
    wx2s = sum(wx * x)
    wys = sum(wy)
    wy2s = sum(wy * y)
    wxys = sum(wx * y)
    ws = sum(w)
    xa = wxs / ws
    x2a = wx2s / ws
    ya = wys / ws
    y2a = wy2s / ws
    xya = wxys / ws

    dx = x2a - xa**2
    dy = y2a - ya**2
    dxy = xya - xa * ya

    a = array([0, dxy / dx])
    a[0] = ya - a[1] * xa
    yfit = a[0] + a[1] * x

    if sig is None:
        chi2 = None
        ws = l * (l - 2) / sum((y - yfit)**2)
    else:
        chi2 = redchi2(y - yfit, sig, 2)

    Da = matrix(zeros([2, 2]))

    Da[1, 1] = 1 / (ws * dx)
    Da[0, 0] = Da[1, 1] * x2a
    s = sqrt(array([Da[0, 0], Da[1, 1]]))
    Da[1, 0] = Da[0, 1] = -Da[1, 1] * xa
    return Ret('a', 's', 'x', 'yfit', 'chi2', cov=Da)

def fitpow(x, y, n, sig=None):
    x = array(x)
    y = array(y)

    l, w = _init_l_w(x, sig)

    x_pow = ones([n + l + 1, l])

    for i in range(1, n + l + 1):
        x_pow[i] = x_pow[i - 1] * x

    wx_pow = x_pow * w
    wyx_pow = y * wx_pow[0:n + 1]

    wx_pow_s = sum(wx_pow, axis=1)
    wyx_pow_s = sum(wyx_pow, axis=1)

    p_matrix = matrix([wx_pow_s[i:i + n + 1] for i in range(0, n + 1)])

    inv_p = p_matrix**-1

    b_matrix = matrix(wx_pow[0:n + 1])

    a = inv_p * matrix(wyx_pow_s).T
    dady = array(inv_p * b_matrix)

    yfit = array(matrix(x_pow[0:n + 1]).T * a).T

    epsilon2 = (y - yfit)**2

    if sig is None:
        chi2 = None
        w = ones(l) * (l - n - 1) / sum(epsilon2)
    else:
        chi2 = sum(epsilon2 * w) / (l - n - 1)

    D2 = matrix([[sum(dady[i] * dady[j] / w) for j in range(0, n + 1)]
                for i in range(0, n + 1)])

    a = array(a).T[0]
    s = sqrt(array([D2[i, i] for i in range(0, n + 1)]))

    func = lambda x: sum([a[i] * pow(x, i) for i in range(0, n + 1)])

    return Ret('a', 's', 'x', 'yfit', 'chi2', 'func', cov=D2)

def fitmlin(x, y, sig=None):
    l, w = _init_l_w(y, sig)
    x = matrix(x)
    y = matrix(y)
    n = len(x)

    W = sum(w)
    wx = multiply(w, x)
    wy = multiply(w, y)

    swx = wx.sum(axis=1)
    swy = wy.sum(axis=1)
    swxy = wx * y.T
    swxx = wx * x.T

    mxx = W * swxx - swx * swx.T
    mxy = W * swxy - swx * swy.T

    a = mxx**-1 * mxy
    b = (swy - a.T * swx) / W

    pright = W * wx - swx * w
    dady = mxx**-1 * pright
    dbdy = (w - swx.T * dady) / W

    yfit = array(a.T * x + b)[0]
    epsilon2 = (array(y)[0] - yfit)**2

    if sig is None:
        chi2 = None
        w = ones(l) * (l - n - 1) / sum(epsilon2)
    else:
        chi2 = sum(epsilon2 * w) / (l - n - 1)

    dbady = r_[dbdy, dady]
    D2 = dbady / w * dbady.T

    a = array(r_[b, a].T)[0]
    s = sqrt(diag(D2))

    return Ret('a', 's', 'yfit', 'chi2', x=array(x), cov=D2)

def fittri(x, y, sig=None, omega=1, maxn=None, ns=None):
    '''
    y = a_0 + \sum_{j}(a_{2j+1}\sin n_jx+a_{2j+2}\cos n_jx)
    '''

    if ns == None:
        if maxn == None:
            ns = array([[1]])
        else:
            ns = array([range(maxn)]).T + 1

    theta = array(x) * omega
    l = len(theta)
    n_l = len(ns)
    ntheta = ns * theta
    sins = sin(ntheta)
    coss = cos(ntheta)
    tris = array([(coss[(i - 1) / 2] if i % 2 else sins[i / 2])
                  for i in range(n_l * 2)])
    lin_fit_res = fitmlin(tris, y, sig)
    lin_fit_res.x = x
    return lin_fit_res

def curve_fit_wrapper(fitfun):
    # http://www.physics.utoronto.ca/~phy326/python/curve_fit_to_data.py
    #     Notes: maxfev is the maximum number of func evaluations tried; you
    #               can try increasing this value if the fit fails.
    #            If the program returns a good chi-squared but an infinite
    #               covariance and no parameter uncertainties, it may be
    #               because you have a redundant parameter;
    #               try fitting with a simpler function.
    def curve_fitter(x, y, sig=None, p0=None):
        a, cov = curve_fit(fitfun, x, y, sigma=sig, p0=p0)
        yfit = fitfun(x, *a)
        func = lambda x: fitfun(x, *a)
        return Ret('x', 'a', 'yfit', 'cov', 'func', s=sqrt(diag(cov)),
                   chi2=redchi2(y - yfit, sig, len(a)) if sig != None else None)
    return curve_fitter
