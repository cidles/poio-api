# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: Peter Bouda <pbouda@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

from __future__ import unicode_literals

from poioapi import data
from graf import GraphParser

class AnnotationGraph():

    def __init__(self, data_structure_type):
        self.data_structure_type = data_structure_type

        if data_structure_type == data.GRAID:
            self.structure_type_handler = data.DataStructureTypeGraid()
        elif data_structure_type == data.GRAIDDIANA:
            self.structure_type_handler = data.DataStructureTypeGraidDiana()
        elif data_structure_type == data.MORPHSYNT:
            self.structure_type_handler = data.DataStructureTypeMorphsynt()
        else:
            self.structure_type_handler = None

        self.graf = None


    def load_graph_from_graf(self, filepath):
        """Load the project annotation graph from a pickle
        file.

        Parameters
        ----------
        filepath : str
            The absolute path to a file.

        """

        parser = GraphParser()
        self.graf = parser.parse(filepath)
