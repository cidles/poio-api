# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

import os

import poioapi.io.elan
import poioapi.io.graf

class SimpleParser(poioapi.io.graf.BaseParser):
    tiers = ["utterance", "word", "wfw", "graid"]

    utterance_tier = ["this is a test", "this is another test"]
    word_tier = [['this', 'is', 'a', 'test'], ['this', 'is', 'another', 'test']]
    wfw_tier = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    graid_tier = ['i', 'j', 'k', 'l', 'm', 'n', 'o', 'p']

    def __init__(self):
        pass

    def get_root_tiers(self):
        return [poioapi.io.graf.Tier("utterance")]

    def get_child_tiers_for_tier(self, tier):
        if tier.name == "utterance":
            return [poioapi.io.graf.Tier("word")]
        if tier.name == "word":
            return [poioapi.io.graf.Tier("graid"), poioapi.io.graf.Tier("wfw")]

        return None

    def get_annotations_for_tier(self, tier, annotation_parent=None):
        if tier.name == "utterance":
            return [poioapi.io.graf.Annotation(i, v) for i, v in enumerate(self.utterance_tier)]

        if tier.name == "word":
            return [poioapi.io.graf.Annotation(2 + 4 * annotation_parent.id + i, v) for i, v
                    in enumerate(self.word_tier[annotation_parent.id])]

        if tier.name == "graid":
            return [poioapi.io.graf.Annotation(annotation_parent.id + 10, self.graid_tier[annotation_parent.id - 2])]

        if tier.name == "wfw":
            return [poioapi.io.graf.Annotation(annotation_parent.id + 12, self.wfw_tier[annotation_parent.id - 2])]

        return []

    def tier_has_regions(self, tier):
        return False

    def region_for_annotation(self, annotation):
        pass


class TestGrAFConverter:
    def setup(self):
        self.parser = SimpleParser()
        self.converter = poioapi.io.graf.GrAFConverter(self.parser)
        self.converter.convert()

        self.graph = self.converter.graph

    def test_get_root_tiers(self):
        assert len(self.parser.get_root_tiers()) == 1

    def test_get_child_tiers_for_tier(self):
        root_tiers = self.parser.get_root_tiers()

        tier = root_tiers[0]

        child_tier = self.parser.get_child_tiers_for_tier(tier)

        assert len(child_tier) == 1

    def test_get_annotations_for_tier(self):
        root_tiers = self.parser.get_root_tiers()

        tier = root_tiers[0]

        child_tier_annotations = self.parser.get_annotations_for_tier(tier)

        assert len(child_tier_annotations) == 2

    def test_get_nodes_from_graf(self):
        nodes = self.graph.nodes

        assert len(nodes) == 26

    def test_get_annotation_from_node(self):
        node = self.graph.nodes['word/n2']
        annotation = node.annotations._elements[0]

        assert annotation.id == 2

    def test_get_edges_from_graf(self):
        edges = self.graph.edges

        assert len(edges) == 18

    def test_get_edge_nodes(self):
        edge = self.graph.edges['e2']

        assert edge.from_node == self.graph.nodes['utterance/n0']
        assert edge.to_node == self.graph.nodes['word/n2']

    def test_get_annotations_spaces_from_graf(self):
        annotation_spaces = self.graph.annotation_spaces

        assert len(annotation_spaces) == 4
        assert len(annotation_spaces['utterance']) == 2
        assert len(annotation_spaces['word']) == 8
        assert len(annotation_spaces['graid']) == 8

    def test_append_tiers_hierarchy(self):
        filename = os.path.join(os.path.dirname(__file__), "sample_files",
            "elan_graf", "example.eaf")

        elan = poioapi.io.elan.Parser(filename)

        converter = poioapi.io.graf.GrAFConverter(elan)
        converter.convert()

        expected_tiers_hierarchy = ['utterance/W-Spch',
            ['words/W-Words',
                ['part_of_speech/W-POS']],
            ['phonetic_transcription/W-IPA']]

        assert expected_tiers_hierarchy == converter.tiers_hierarchy[2]
