# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
""" This module is to create a GrAF file from
the Annotation Tree data hierarchies.
"""

from graf.PyGrafRenderer import PyGrafRenderer
from graf.PyGraphParser import PyGraphParser
import os

class RendToGrAF():
    """
    Class to rend the files from the Annotation Tree to GrAF.

    """

    def __init__(self, filepath):
        """Class's constructor.

        Parameters
        ----------
        filepath : str
            Path of the file to manipulate.

        """

        self.filepath = filepath

    def parse_xml_graf(self, type):
        """Parsing of the file of the given type to
        GrAF xml file.

        Parameters
        ----------
        type : str
            Type is the components of each data hierarchies,
            like wfw, morpheme, graid 1 and graid 2.

        """

        basename = self.filepath.split('.pickle')
        file = os.path.abspath(basename[0])
        parser = PyGraphParser()
        g = parser.parse(file + '-' + str(type) + '.xml')

        # Rendering the Graph
        graf_render = PyGrafRenderer(file + '-rend.xml')
        graf_render.render(g)