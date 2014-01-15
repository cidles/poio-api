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

import poioapi.io.toolbox
import poioapi.io.graf

class TestParser:
    """
    This class contain the test methods to the
    class io.toolbox.py.

    """

    def setup(self):
        self.filename = os.path.join(os.path.dirname(__file__), "..",
        	"sample_files", "toolbox_graf", "toolbox.txt")
        self.parser = poioapi.io.toolbox.Parser(self.filename, "ref")

    def test_tier_hierachy(self):
        assert self.parser.tier_hierarchy.data_hierarchy == \
            ['ref', [ 'utterance_gen', ['tx', ['mb', ['ge', 'ps']]],
                ['ft', 'nt', 'rf', 'rt', 'graid']],
                ['id', 'dt']]

    def test_get_root_tiers(self):
        root_tiers = self.parser.get_root_tiers()
        assert len(root_tiers) == 1

    def test_get_child_tiers_for_tier(self):
        root_tiers = self.parser.get_root_tiers()

        child_tiers = self.parser.get_child_tiers_for_tier(root_tiers[0])
        assert len(child_tiers) == 3

        child_tiers = self.parser.get_child_tiers_for_tier(
            poioapi.io.graf.Tier('tx'))
        assert len(child_tiers) == 1


    def test_get_annotations_for_tier(self):
        root_tiers = self.parser.get_root_tiers()
        root_annotations = self.parser.get_annotations_for_tier(root_tiers[0])

        assert len(root_annotations) == 295

        tier = poioapi.io.graf.Tier("utterance_gen")
        annotation_parent = root_annotations[0]
        assert annotation_parent.value == "Pear_Madi.001"
        assert annotation_parent.id == "a0"

        tier_annotations = self.parser.get_annotations_for_tier(
            tier, annotation_parent)

        assert len(tier_annotations) == 1

        tier = poioapi.io.graf.Tier("tx")
        annotation_parent = tier_annotations[0]
        assert annotation_parent.value == "diž yikes . diž bikes čeq čeqi rekʼe"

        tier_annotations = self.parser.get_annotations_for_tier(
            tier, annotation_parent)

        assert len(tier_annotations) == 8
