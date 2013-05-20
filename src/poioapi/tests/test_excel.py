# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

import os
import codecs
import sys

import poioapi.annotationgraph
import poioapi.io.excel
import poioapi.io.graf

class TestExcel:
    """
    This class contain the test methods to the
    class io.excel.py.

    """

    def setup(self):
        self.filename = os.path.join(os.path.dirname(__file__), "sample_files",
            "excel_graf", "Hinuq2.csv")

        self.filepath = self.open_file_(self.filename)

        self.excel = poioapi.io.excel.Parser(self.filepath)

        headerfile = os.path.join(os.path.dirname(__file__), "sample_files",
            "excel_graf", "Hinuq2.hdr")

        self.annotation_graph = poioapi.annotationgraph.AnnotationGraph(None)
        self.annotation_graph.load_graph_from_graf(headerfile)

    def open_file_(self, filename):
        if sys.version_info[:2] >= (3, 0):
            return codecs.open(filename, "r", "utf-8")
        else:
            return open(filename, "r")

    def test_get_root_tiers(self):
        root_tiers = self.excel.get_root_tiers()

        assert len(root_tiers) == 1
        assert root_tiers[0].name == "ref"

    def test_get_child_tiers_for_tier(self):
        root_tiers = self.excel.get_root_tiers()
        root_tier = root_tiers[0]
        child_tiers = self.excel.get_child_tiers_for_tier(root_tier)

        assert len(child_tiers) == 1
        assert child_tiers[0].name == "clause_id"

        tier = poioapi.io.graf.Tier('word')
        child_tiers = self.excel.get_child_tiers_for_tier(tier)

        assert len(child_tiers) == 4
        assert child_tiers[0].name == "grammatical_relation"

    def test_get_annotations_for_tier(self):
        tier = poioapi.io.graf.Tier('ref')
        tier_annotations = self.excel.get_annotations_for_tier(tier)

        assert len(tier_annotations) == 10

    def test_get_annotations_for_tier_with_parent(self):
        root_tiers = self.excel.get_root_tiers()
        child_tiers = self.excel.get_child_tiers_for_tier(root_tiers[0])

        parent_annotation = poioapi.io.graf.Annotation('1', "XoddonBarun.001")
        child_tier_annotations = self.excel.get_annotations_for_tier(child_tiers[0],
            parent_annotation)

        assert len(child_tier_annotations) == 3
        assert child_tier_annotations[0].id == "#1"
        assert child_tier_annotations[2].id == "#3"

    def test_get_annotations_from_list(self):
        annotation_parent = poioapi.io.graf.Annotation('1', "XoddonBarun.001")
        annotations = self.excel._get_annotations_from_list(2, annotation_parent.id)

        assert len(annotations) == 3
        assert annotations[0].id == "#1"
        assert annotations[1].id == "#2"
        assert annotations[2].id == "#3"