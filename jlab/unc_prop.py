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

def _uncp_prep_arg(a, s=None, cov=None):
    a = array(a)
    l = a.size
    covm = matrix(zeros([l, l]))
    if cov != None:
        covm = matrix(cov)[0:l, 0:l]
    elif s:
        covm = matrix(diag(a))

    return Ret('a', cov=covm)

def uncp_add(a, s=None, cov=None):
    args = _uncp_prep_arg(a, s, cov)
    a = args.a
    cov = args.cov

def uncp_div(a, s=None, cov=None):
    args = _uncp_prep_arg(a, s, cov)
    a0 = args.a
    cov = args.cov

    a = a0[0] / a0[1]
    rel_s = sqrt(sum(abs2relcov(a0, cov)[:1, :1]))
    s = abs(rel_s * a)
    return Ret('a', 's')

def abs2relcov(a, cov):
    return (matrix(cov).T / a).T / a

def rel2abscov(a, cov):
    return matrix((array(cov).T * a).T * a)
