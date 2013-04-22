# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#cd
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
        # Initialize the AnnotationTree class
        self.annotation_graph = poioapi.annotationgraph.AnnotationGraph(
            data.DataStructureTypeGraid())

        filename = os.path.join(os.path.dirname(__file__), "sample_files",
            "balochi_graf", "balochi.hdr")
        self.annotation_graph.load_graph_from_graf(filename)

    def test_load_graph_from_graf(self):
        expected_nodes = 1161
        assert(len(self.annotation_graph.graf.nodes) == expected_nodes)

    def test_root_nodes(self):
        root_nodes = self.annotation_graph.root_nodes()
        assert(len(root_nodes) == 111)

    def test_nodes_for_tier(self):
        root_nodes = self.annotation_graph.root_nodes()
        clause_units = self.annotation_graph.nodes_for_tier("clause_unit", root_nodes[0])
        assert(len(clause_units) == 1)

    def test_annotations_for_tier(self):
        node = self.annotation_graph.graf.nodes["word/n1"]
        annotations = self.annotation_graph.annotations_for_tier("wfw", node)
        assert(len(annotations) == 1)

    def test_annotation_value_for_annotation(self):
        node = self.annotation_graph.graf.nodes["word/n1"]
        annotations = self.annotation_graph.annotations_for_tier("wfw", node)
        value = self.annotation_graph.annotation_value_for_annotation(annotations[0])
        assert(value=="say.PRS-3SG")

    def test_as_html_table(self):
        html = self.annotation_graph.as_html_table()
        assert(len(html) > 0)


class AnnotationGraphFilter:

    def test_element_passes_filter(self):
        # Open the file and set it to the AnnotationTree
        data_structure_type = data.DataStructureTypeGraid()
        anngraphfilter = poioapi.annotationgraph.AnnotationGraphFilter(data_structure_type)
        anngraphfilter.set_filter_for_type("graid2", "nc")

        # If the variables value equal like this
        element = [{'id': 6, 'annotation': 'gu\u0161-\u012bt:'},
            [[{'id': 4, 'annotation': 'gu\u0161-\u012bt:'},
                [[{'id': 1, 'annotation': 'gu\u0161-\u012bt:'},
                        {'id': 2, 'annotation': 'say.PRS-3SG'},
                        {'id': 3, 'annotation': ''}]],
                    {'id': 5, 'annotation': 'nc'}]],
                {'id': 7, 'annotation': 'They say:'},
                {'id': 8, 'annotation': ''}]

        # The result expected should be
        expected_result = True # Boolean value

        assert(anngraphfilter.element_passes_filter(element)
               == expected_result)