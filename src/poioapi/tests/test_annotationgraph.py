# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: Peter Bouda <pbouda@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

import os

from poioapi import data
import poioapi.annotationgraph

class TestAnnotationGraph:
    """
    This class contain the test methods to the
    class annotationgraph.py.

    """

    def setup(self):
        # Initialize the DataStructureType class
        self.data_structure_type = data.DataStructureTypeGraid()

        # Initialize the AnnotationTree class
        self.annotation_graph = poioapi.annotationgraph.AnnotationGraph(
            self.data_structure_type)

    def test_load_graph_from_graf(self):
        filename = os.path.join(os.path.dirname(__file__), "sample_files",
            "balochi_graf", "balochi.hdr")
        self.annotation_graph.load_graph_from_graf(filename)

        expected_nodes = 618
        assert(len(self.annotation_graph.graf.nodes) == expected_nodes)

    def test_get_all_neighbours_for_node(self):
        filename = os.path.join(os.path.dirname(__file__), "sample_files",
            "balochi_graf", "balochi.hdr")
        self.annotation_graph.load_graph_from_graf(filename)

        clause_units = self.annotation_graph.get_all_neighbours_for_node("utterance-n1", "clause unit")
        assert(clause_units == [ "clause_unit-n1" ])