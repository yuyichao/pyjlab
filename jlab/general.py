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

from __future__ import print_function
from pylab import *
from numpy import power
from scipy.interpolate import spline #for smooth plot
import os
from os import path
import sys
import inspect

#stolen from https://github.com/gak/automain
#note: BDFL hates this http://www.python.org/dev/peps/pep-0299/
def automain(func):
    '''
    Limitation: the main function can only be defined at the end of the file.
    '''
    import inspect
    parent = inspect.stack()[1][0]
    name = parent.f_locals.get('__name__', None)
    if name == '__main__':
        func()
    return func

class Ret(object):
    def __init__(self, *args, **kwargs):
        object.__setattr__(self, '__dict__', {})
        for arg in args:
            try:
                self._a(**arg)
            except:
                frame = inspect.currentframe().f_back
                pair = {arg: eval(arg, frame.f_globals, frame.f_locals)}
                self._a(**pair)
        self._a(**kwargs)
    def _a(self, **kwargs):
        for k, v in kwargs.items():
            self[k] = v
        return self
    def __getattr__(self, key):
        try:
            return self.__dict__[key]
        except KeyError:
            raise AttributeError(key)
    def __setattr__(self, key, value):
        real = False
        if hasattr(Ret, key):
            raise AttributeError
        self.__dict__[key] = value
    def __delattr__(self, name):
        pass
    def __getitem__(self, keys):
        if issubclass(type(keys), str):
            return self.__dict__[keys]
        res = ()
        for k in keys:
            res += (getattr(self, k, None),)
        return res
    def __setitem__(self, keys, items):
        if type(keys) == type(()):
            for i in range(0, len(keys)):
                setattr(self, keys[i], items[i])
            return
        setattr(self, keys, items)
    def __delitem__(self, name):
        pass
    def __repr__(self):
        return "Ret(%s)" % self.__dict__
    def __str__(self):
        return str(self.__dict__)
    def __iter__(self):
        return iter(self.__dict__)

    def keys(self):
        return self.__dict__.keys()
    def items(self):
        return self.__dict__.items()
    def values(self):
        return self.__dict__.values()

def a_pm_s(a_s, unit='', sci=None, tex=False):
    try:
        a = a_s.a
        s = a_s.s
    except AttributeError:
        try:
            a = a_s[0]
            s = a_s[1]
        except KeyError:
            a = a_s['a']
            s = a_s['s']

    try:
        a = [i for i in a]
        l = len(a)
    except TypeError:
        a = [a]
        l = 1

    try:
        s = [i for i in s]
    except TypeError:
        s = [s]

    if len(s) < l:
        s += [0] * (l - len(s))

    if type(unit) == type(''):
        unit = [unit] * l
    else:
        try:
            unit = [u for u in unit]
        except TypeError:
            unit = [unit] * l

    if len(unit) < l:
        unit += [''] * (l - len(unit))
    if l == 1:
        return _a_pm_s(a[0], s[0], unit[0], sci, tex)
    return array([_a_pm_s(a[i], s[i], unit[i], sci, tex) for i in range(0, l)])

def _a_pm_s(a, s, unit, sci, tex):
    '''input: observable,error
       output: formatted observable +- error in scientific notation'''
    if s <= 0:
        return '%f%s' % (a, unit)

    if sci == None:
        if s < 100 and (abs(a) > 1 or s > 1):
            sci = False
        else:
            sci = True

    la = int(floor(log10(abs(a))))
    ls = int(floor(log10(s)))
    fs = floor(s * 10**(1 - ls))
    if sci:
        fa = a * 10**-la
        dl = la - ls + 1
    else:
        fa = a
        dl = 1 - ls
    dl = dl if dl > 0 else 0

    if dl == 1:
        ss = '%.1f' % (fs / 10)
    else:
        ss = '%.0f' % fs

    if sci:
        if tex:
            return (('%.' + ('%d' % dl) + r'f(%s)\times10^{%d}{%s}') %
                    (fa, ss, la, unit))
        else:
            return ('%.' + ('%d' % dl) + 'f(%s)*10^%d%s') % (fa, ss, la, unit)
    else:
        return ('%.' + ('%d' % dl) + 'f(%s)%s') % (fa, ss, unit)

# Don't use when plotting a function.
# And probably don't need to use when plotting data.
def smoothplot(x, y, *args, **kwargs):
    '''because pylab doesn't know how to plot smoothly out of the box yet'''
    # http://stackoverflow.com/questions/5283649/plot-smooth-line-with-pyplot
    # wrapper for plot to make it smooth
    xnew = np.linspace(x.min(), x.max(), 300)
    ynew = spline(x, y, xnew)
    return plot(xnew, ynew, *args, **kwargs)

def redchi2(delta, sigma, n):
    '''chi2 / dof'''
    return sum((delta / sigma)**2) / (delta.size - n)

def py2ret(fname):
    '''
    Read the namespace of a pyfile to a Ret object.
    '''
    gs = {}
    ls = {}
    with open(fname, "r") as fh:
        code = compile(fh.read() + "\n", fname, 'exec')
    exec(code, gs, ls)
    return Ret(ls)

def saveiter(obj, fname):
    '''
    Save members of a iterable object to a .py file.
    '''
    if not hasattr(obj, '__getitem__'):
        return
    with open(fname, "w") as fh:
        for key in obj:
            fh.write("%s = %s\n" % (key, repr(obj[key])))

def frel2abs(rel_fname):
    '''
    Turn a filename relative to caller's file location to absolute path.
    Directly return if it is already an absolute path.
    '''
    if path.isabs(rel_fname):
        return rel_fname
    import inspect
    f = inspect.currentframe().f_back
    try:
        caller_f = eval('__file__', f.f_globals, f.f_locals)
        dirname = path.dirname(path.abspath(caller_f))
    except NameError:
        dirname = '.'
    return path.abspath('%s/%s' % (dirname, rel_fname))

# FIXME also return lambda in fit functions
def showfit(data, fitobj):
    '''
    Just because plotting scatter(data) and plot(x,yfit)
    simultaneously is a very often-used idiom
    '''
    x, y, s = data
    errorbar(x, y, s, fmt='o')
    plot(fitobj.x, fitobj.yfit)
