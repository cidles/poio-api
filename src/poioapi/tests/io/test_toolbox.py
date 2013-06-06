# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

import os

import poioapi.io.toolbox
import poioapi.io.graf


class TestToolbox:
    """
    This class contain the test methods to the
    class io.toolbox.py.

    """

    def setup(self):
        self.filename = os.path.join(os.path.dirname(__file__), "..", "sample_files",
            "toolbox_graf", "toolbox.xml")

        self.basedirname = os.path.dirname(self.filename)

        self.parser = poioapi.io.toolbox.Parser(self.filename)

    def test_get_root_tiers(self):
        root_tiers = self.parser.get_root_tiers()

        assert len(root_tiers) == 1

    def test_get_child_tiers_for_tier(self):
        root_tiers = self.parser.get_root_tiers()
        child_tier = self.parser.get_child_tiers_for_tier(root_tiers[0])

        assert len(child_tier) == 1
        assert child_tier[0].name == "idGroup"

        tier = poioapi.io.graf.Tier("tx")
        child_tiers = self.parser.get_child_tiers_for_tier(tier)

        assert len(child_tiers) == 2
        assert child_tiers[0].name == "mr"
        assert child_tiers[1].name == "mg"

    def test_get_annotations_for_tier(self):
        root_tiers = self.parser.get_root_tiers()
        root_annotations = self.parser.get_annotations_for_tier(root_tiers[0])

        assert len(root_annotations) == 70

        tier = poioapi.io.graf.Tier("idGroup")
        annoation_parent = root_annotations[0]

        tier_annotations = self.parser.get_annotations_for_tier(tier, annoation_parent)

        assert len(tier_annotations) == 29

    def test_tier_has_regions(self):
        tier = poioapi.io.graf.Tier("tx")
        has_regions = self.parser.tier_has_regions(tier)

        assert not has_regions

        tier = poioapi.io.graf.Tier("idGroup")
        has_regions = self.parser.tier_has_regions(tier)

        assert has_regions

    def test_region_for_annotation(self):
        root_tiers = self.parser.get_root_tiers()
        root_annotations = self.parser.get_annotations_for_tier(root_tiers[0])

        tier = poioapi.io.graf.Tier("idGroup")
        annoation_parent = root_annotations[0]
        annotations = self.parser.get_annotations_for_tier(tier, annoation_parent)

        regions = self.parser.region_for_annotation(annotations[0])
        expected_regions = ('905.88', '917.4')

        assert regions == expected_regions