# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

from __future__ import unicode_literals

import os

import poioapi.io.shoebox
import poioapi.io.graf


class TestParser:
    """
    This class contain the test methods to the
    class io.shoebox.py.

    """

    def setup(self):
        self.filename = os.path.join(os.path.dirname(__file__), "..",
                                     "sample_files", "shoebox_graf", "shoebox.xml")
        self.parser = poioapi.io.shoebox.Parser(self.filename)

    def test_get_root_tiers(self):
        root_tiers = self.parser.get_root_tiers()
        assert len(root_tiers) == 1

    def test_get_child_tiers_for_tier(self):
        root_tiers = self.parser.get_root_tiers()

        child_tiers = self.parser.get_child_tiers_for_tier(root_tiers[0])
        assert len(child_tiers) == 1

        child_tiers = self.parser.get_child_tiers_for_tier(
            poioapi.io.graf.Tier('m'))
        assert len(child_tiers) == 1


    def test_get_annotations_for_tier(self):
        root_tiers = self.parser.get_root_tiers()
        root_annotations = self.parser.get_annotations_for_tier(root_tiers[0])

        assert len(root_annotations) == 1

        tier = poioapi.io.graf.Tier("t")
        annotation_parent = root_annotations[0]
        assert annotation_parent.value == "Baho katali difisi na sungula hawowa mbuya kamei sungula kamgamba, chigende nhambo. "
        assert annotation_parent.id == "mjs3001revised"

        tier_annotations = self.parser.get_annotations_for_tier(
            tier, annotation_parent)

        assert len(tier_annotations) == 12

        tier = poioapi.io.graf.Tier("p")
        annotation_parent = tier_annotations[0]
        assert annotation_parent.value == "Baho"

        tier_annotations = self.parser.get_annotations_for_tier(
            tier, annotation_parent)

        assert len(tier_annotations) == 1
