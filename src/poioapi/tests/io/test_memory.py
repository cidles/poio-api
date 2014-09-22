# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2014 Poio Project
# Author: Peter Bouda <pbouda@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

import poioapi.io.memory
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
        if tier.name == "utterance":
            return True
        return False

    def region_for_annotation(self, annotation):
        if annotation.id == 0:
            return (0, 100)
        elif annotation.id == 1:
            return (101, 200)

    def get_primary_data(self):
        pass

class TestGrAFConverter:
    def setup(self):
        self.parser = SimpleParser()
        self.converter = poioapi.io.memory.MemoryConverter(self.parser)
        self.converter.parse()

    def test_tier_hierarchies(self):
        assert(
            self.converter.tier_hierarchies == \
                [['utterance', ['word', ['graid'], ['wfw']]]])

    def test_region_for_annotations(self):
        assert(self.converter.region_for_annotation == \
            {0: (0, 100), 1: (101, 200)})
