# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: Peter Bouda <pbouda@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

from __future__ import unicode_literals

import os

from poioapi import data
import poioapi.annotationgraph

class DataStructureTypeElan(poioapi.data.DataStructureType):
    name = "ELAN"

    data_hierarchy =\
    [ 'Äußerung',
        [ 'Wort',
            [ 'Morphem',
                [ 'Glosse' ],
              ]
        ],
      'Übersetzung']

class TestAnnotationGraph:
    """
    This class contain the test methods to the
    class annotationgraph.py.

    """

    def setup(self):
        self.annotation_graph = poioapi.annotationgraph.AnnotationGraph(DataStructureTypeElan())

        filename = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..',
            '..', '..', 'example_data', 'turkish.eaf'))

        self.annotation_graph.from_elan(filename)
        self.annotation_graph.init_filters()

        self.anngraphfilter = poioapi.annotationgraph.AnnotationGraphFilter(
            self.annotation_graph)

    def test_root_nodes(self):
        root_nodes = self.annotation_graph.root_nodes()
        assert(len(root_nodes) == 9)

    def test_nodes_for_tier(self):
        root_nodes = self.annotation_graph.root_nodes()
        nodes = self.annotation_graph.nodes_for_tier("Äußerung", root_nodes[0])
        
        assert(len(nodes) == 0)

    def test_annotations_for_tier(self):
        node = self.annotation_graph.graf.nodes["Glosse/P-Gloss/na262"]
        annotations = self.annotation_graph.annotations_for_tier("Glosse", node)
        assert(len(annotations) == 1)

    def test_annotation_value_for_annotation(self):
        node = self.annotation_graph.graf.nodes["Glosse/P-Gloss/na262"]
        annotations = self.annotation_graph.annotations_for_tier("Glosse", node)
        value = self.annotation_graph.annotation_value_for_annotation(annotations[0])
        assert(value=="REPPAST")

    def test_as_html_table(self):
        html = self.annotation_graph.as_html_table()
        assert(len(html) > 0)

    def test_append_filter(self):
        self.anngraphfilter.set_filter_for_type("Glosse", "ANOM")
        self.annotation_graph.append_filter(self.anngraphfilter)
        self.anngraphfilter.reset_match_object()

        print(self.annotation_graph.filtered_node_ids)

        assert self.annotation_graph.filtered_node_ids[-1] == ['Äußerung/P-Spch/na2', 'Äußerung/P-Spch/na9']

    def test_reset_filters(self):
        self.anngraphfilter.set_filter_for_type("Glosse", "ANOM")
        self.annotation_graph.append_filter(self.anngraphfilter)
        self.anngraphfilter.reset_match_object()

        assert self.annotation_graph.filtered_node_ids[-1] == ['Äußerung/P-Spch/na2', 'Äußerung/P-Spch/na9']

    def test_create_filter_for_dict(self):
        search_terms = { "Glosse": "yesterday" }
        self.anngraphfilter = self.annotation_graph.create_filter_for_dict(search_terms)
        self.annotation_graph.append_filter(self.anngraphfilter)
        self.anngraphfilter.reset_match_object()

        assert self.annotation_graph.filtered_node_ids[-1] == ['Äußerung/P-Spch/na1']

class TestAnnotationGraphFilter:

    def setup(self):
        self.annotation_graph = poioapi.annotationgraph.AnnotationGraph(
            data.DataStructureTypeGraid())

        filename = os.path.join(os.path.dirname(__file__), "sample_files",
            "balochi_graf", "balochi.hdr")
        self.annotation_graph.from_graf(filename)

        self.data_structure_type = data.DataStructureTypeGraid()
        self.anngraphfilter = poioapi.annotationgraph.AnnotationGraphFilter(self.annotation_graph)

    def test_element_passes_filter(self):
        self.anngraphfilter.set_filter_for_type("graid2", "nc")

        element = self.annotation_graph.graf.nodes['utterance/n898']
        expected_result = False

        assert(self.anngraphfilter.element_passes_filter(element)
               == expected_result)

        element = self.annotation_graph.graf.nodes['utterance/n6']
        expected_result = True

        assert(self.anngraphfilter.element_passes_filter(element)
               == expected_result)

        #element = self.annotation_graph.graf.nodes['utterance/n89']
        self.anngraphfilter.set_filter_for_type("graid2", "")
        self.anngraphfilter.set_filter_for_type("clause_unit", "nc")
        expected_result = False

        assert(self.anngraphfilter.element_passes_filter(element)
               == expected_result)
