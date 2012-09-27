# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT

from graf.PyGrafRenderer import PyGrafRenderer
from graf.PyGraphParser import PyGraphParser

class RendToGrAF():

    def __init__(self, filepath):
        self.filepath = filepath

    def parse_xml_graf(self, type):
        """
        """
        parser = PyGraphParser()
        g = parser.parse(self.filepath.replace('.pickle',
            '-' + str(type) + '.xml'))

        # Rendering the Graph
        graf_render = PyGrafRenderer(self.filepath + '-rend.xml')
        graf_render.render(g)