# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: Peter Bouda <pbouda@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

import os
import re

from poioapi import data
import poioapi.annotationgraph

class TestAnnotationGraph:
    """
    This class contain the test methods to the
    class annotationgraph.py.

    """

    def setup(self):
        self.annotation_graph = poioapi.annotationgraph.AnnotationGraph(
            data.DataStructureTypeGraid())

        filename = os.path.join(os.path.dirname(__file__), "sample_files",
            "balochi_graf", "balochi.hdr")
        self.annotation_graph.load_graph_from_graf(filename)

        self.anngraphfilter = poioapi.annotationgraph.AnnotationGraphFilter(
            data.DataStructureTypeGraid())

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

    def test_append_filter(self):
        self.anngraphfilter.set_filter_for_type("clause_unit", "nc")
        self.annotation_graph.append_filter(self.anngraphfilter)

        assert self.annotation_graph.filtered_node_ids == [['utterance/n1207', 'utterance/n6']]

    def test_reset_filters(self):
        self.anngraphfilter.set_filter_for_type("clause_unit", "nc")
        self.annotation_graph.append_filter(self.anngraphfilter)
        self.anngraphfilter.reset_match_object()

        assert self.annotation_graph.filtered_node_ids == [['utterance/n1207', 'utterance/n6']]

class TestAnnotationGraphFilter:

    def setup(self):
        self.annotation_graph = poioapi.annotationgraph.AnnotationGraph(
            data.DataStructureTypeGraid())

        filename = os.path.join(os.path.dirname(__file__), "sample_files",
            "balochi_graf", "balochi.hdr")
        self.annotation_graph.load_graph_from_graf(filename)

        self.data_structure_type = data.DataStructureTypeGraid()
        self.anngraphfilter = poioapi.annotationgraph.AnnotationGraphFilter(self.data_structure_type)

    def test_element_passes_filter(self):
        self.anngraphfilter.set_filter_for_type("clause_unit", "nc")

        element = self.annotation_graph.graf.nodes
        expected_result = True

        assert(self.anngraphfilter.element_passes_filter(element)
               == expected_result)

        element = self.annotation_graph.graf.nodes['clause_unit/n1001']
        expected_result = False

        assert(self.anngraphfilter.element_passes_filter(element)
               == expected_result)