# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2014 Poio Project
# Author: Peter Bouda <pbouda@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

import os

import poioapi.io.obt

class TestParser:
    """
    This class contain the test methods to the
    class io/obt.py.

    """

    def setup(self):
        self.filename = os.path.join(os.path.dirname(__file__), "..",
            "sample_files", "obt", "suite_fotball.xml")

        self.parser = poioapi.io.obt.Parser(self.filename)

    def test_get_root_tiers(self):
        root_tiers = self.parser.get_root_tiers()
        assert len(root_tiers) == 1

    def test_get_child_tiers_for_tier(self):
        root_tiers = self.parser.get_root_tiers()

        child_tiers = self.parser.get_child_tiers_for_tier(root_tiers[0])
        assert len(child_tiers) == 1

        child_tiers = self.parser.get_child_tiers_for_tier(
            poioapi.io.graf.Tier('word'))
        assert len(child_tiers) == 1

    def test_get_annotations_for_tier(self):
        root_tiers = self.parser.get_root_tiers()
        root_annotations = self.parser.get_annotations_for_tier(root_tiers[0])

        assert len(root_annotations) == 101

        tier = poioapi.io.graf.Tier("word")
        annotation_parent = root_annotations[0]
        assert annotation_parent.value == \
            "I Strømsgodset-stallen er det bare to spillere som kan skilte med millioninntekt fra 2012 ."
        assert annotation_parent.id == "a0"

        tier_annotations = self.parser.get_annotations_for_tier(
            tier, annotation_parent)

        assert len(tier_annotations) == 15
