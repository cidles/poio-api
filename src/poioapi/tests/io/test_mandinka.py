# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2014 Poio Project
# Author: Peter Bouda <pbouda@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

import os
import codecs

import poioapi.io.mandinka
import poioapi.data
import poioapi.mapper

tier_map = {
    poioapi.data.TIER_UTTERANCE: "utterance_gen",
    poioapi.data.TIER_WORD: "t",
    poioapi.data.TIER_MORPHEME: "m",
    poioapi.data.TIER_POS: "p",
    poioapi.data.TIER_GLOSS: "g",
    poioapi.data.TIER_TRANSLATION: "f",
    poioapi.data.TIER_COMMENT: "nt"
}

class TestParser:
    """
    This class contain the test methods to the
    class io/mandinka.py.

    """

    def setup(self):
        self.filename = os.path.join(os.path.dirname(__file__), "..",
            "sample_files", "mandinka", "mandinka.txt")

        self.parser = poioapi.io.mandinka.Parser(self.filename, None)

    def test_get_root_tiers(self):
        root_tiers = self.parser.get_root_tiers()
        assert len(root_tiers) == 1

    def test_get_child_tiers_for_tier(self):
        root_tiers = self.parser.get_root_tiers()

        child_tiers = self.parser.get_child_tiers_for_tier(root_tiers[0])
        assert len(child_tiers) == 2

        child_tiers = self.parser.get_child_tiers_for_tier(
            poioapi.io.graf.Tier(poioapi.data.tier_labels[poioapi.data.TIER_WORD]))
        assert len(child_tiers) == 1

    def test_get_annotations_for_tier(self):
        root_tiers = self.parser.get_root_tiers()
        root_annotations = self.parser.get_annotations_for_tier(root_tiers[0])
        assert len(root_annotations) == 7

        tier = poioapi.io.graf.Tier(poioapi.data.tier_labels[poioapi.data.TIER_WORD])
        annotation_parent = root_annotations[0]
        result = 'Musukéebâa níŋ a lá maañóo le táatá lóoñínóo la.'
        result = codecs.encode(result)

        assert codecs.encode(annotation_parent.value) == result
        assert annotation_parent.id == "a0"

        tier_annotations = self.parser.get_annotations_for_tier(
            tier, annotation_parent)

        assert len(tier_annotations) == 9