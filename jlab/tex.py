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

import os
from os import path
from .general import *

default_temp = r'''
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsfonts}
\usepackage{picinpar}
\usepackage[pdftex]{graphicx}
\usepackage{wrapfig}
\usepackage{units}
\usepackage{textcomp}
\usepackage[utf8x]{inputenc}
\usepackage{feyn}
\usepackage{feynmp}
\newcommand{\ud}{\mathrm{d}}
\newcommand{\ue}{\mathrm{e}}
\newcommand{\ui}{\mathrm{i}}
\newcommand{\res}{\mathrm{Res}}
\newcommand{\Tr}{\mathrm{Tr}}
\newcommand{\dsum}{\displaystyle\sum}
\newcommand{\dprod}{\displaystyle\prod}
\newcommand{\dlim}{\displaystyle\lim}
\newcommand{\dint}{\displaystyle\int}
\newcommand{\fsno}[1]{{\!\not\!{#1}}}
\newcommand{\texp}[2]{\ensuremath{{#1}\times10^{#2}}}
\newcommand{\dexp}[2]{\ensuremath{{#1}\cdot10^{#2}}}
\newcommand{\eval}[2]{{\left.{#1}\right|_{#2}}}
\newcommand{\paren}[1]{{\left({#1}\right)}}
\newcommand{\lparen}[1]{{\left({#1}\right.}}
\newcommand{\rparen}[1]{{\left.{#1}\right)}}
\newcommand{\abs}[1]{{\left|{#1}\right|}}
\newcommand{\sqr}[1]{{\left[{#1}\right]}}
\newcommand{\crly}[1]{{\left\{{#1}\right\}}}
\newcommand{\angl}[1]{{\left\langle{#1}\right\rangle}}
\newcommand{\tpdiff}[4][{}]{{\paren{\frac{\partial^{#1} {#2}}{\partial {#3}{}^{#1}}}_{#4}}}
\newcommand{\tpsdiff}[4][{}]{{\paren{\frac{\partial^{#1}}{\partial {#3}{}^{#1}}{#2}}_{#4}}}
\newcommand{\pdiff}[3][{}]{{\frac{\partial^{#1} {#2}}{\partial {#3}{}^{#1}}}}
\newcommand{\diff}[3][{}]{{\frac{\ud^{#1} {#2}}{\ud {#3}{}^{#1}}}}
\newcommand{\psdiff}[3][{}]{{\frac{\partial^{#1}}{\partial {#3}{}^{#1}} {#2}}}
\newcommand{\sdiff}[3][{}]{{\frac{\ud^{#1}}{\ud {#3}{}^{#1}} {#2}}}
\newcommand{\tpddiff}[4][{}]{{\left(\dfrac{\partial^{#1} {#2}}{\partial {#3}{}^{#1}}\right)_{#4}}}
\newcommand{\tpsddiff}[4][{}]{{\paren{\dfrac{\partial^{#1}}{\partial {#3}{}^{#1}}{#2}}_{#4}}}
\newcommand{\pddiff}[3][{}]{{\dfrac{\partial^{#1} {#2}}{\partial {#3}{}^{#1}}}}
\newcommand{\ddiff}[3][{}]{{\dfrac{\ud^{#1} {#2}}{\ud {#3}{}^{#1}}}}
\newcommand{\psddiff}[3][{}]{{\frac{\partial^{#1}}{\partial{}^{#1} {#3}} {#2}}}
\newcommand{\sddiff}[3][{}]{{\frac{\ud^{#1}}{\ud {#3}{}^{#1}} {#2}}}
'''

class Tex():
    def __init__(self, text='', temp=None, klass='standalone'):
        if temp == None:
            temp = default_temp
        self.temp = temp
        self.klass = klass
        self.text = text
    def content(self):
        return ("\\documentclass{%s}\n%s\\begin{document}\n%s\n\\end{document}" %
                (self.klass, self.temp, self.text))
    def addform(self, form):
        form_txt = '\n\\hline\n'
        j = 0
        for row in form:
            i = 0
            for col in row:
                form_txt += "%s&" % col
                i += 1
            form_txt = form_txt[:-1] + '\\\\\\hline\n'
            j = i if i > j else j
        self.text += (r'\ensuremath{\begin{array}{%s}%s\end{array}}'
                      % ('|c' * j + '|', form_txt))
    def pdf_w(self, fname):
        dir_name = path.dirname(fname)
        fname = path.basename(fname)
        if dir_name == '':
            dir_name = '.'
        if fname.endswith('.pdf'):
            jname = fname[:-4]
        else:
            jname = fname
        f = os.popen('pdflatex -output-directory %s -jobname %s &>/dev/null'
                     % (dir_name, jname), 'w')
        f.write(self.content())
        f.close()

def print_array(fname, table, head=None):
    tex = Tex()
    f_table = array(table)
    if head:
        head = array(head)
        head = head.reshape(head.size)
        f_table = array([head.tolist()] + f_table.T.tolist()).T
    tex.addform(f_table)
    tex.pdf_w(fname)
