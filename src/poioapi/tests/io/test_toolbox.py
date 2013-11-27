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

class TestToolboxLine:

    def setup(self):
        self.line = "\mb diž y-   ike -s   .     diž b-   ike -s   čeq  čeq  -i      rekʼe"
        self.toolbox_line = poioapi.io.toolbox.ToolboxLine(self.line)

    def test_char_len(self):
     	assert poioapi.io.toolbox.ToolboxLine.char_len(self.line) == 70

    def test_line_string(self):
     	assert self.toolbox_line.line_original == self.toolbox_line.line_string

    def test_words(self):
        assert self.toolbox_line.words() == \
            ['diž', 'y-   ike -s', '.', 'diž', 'b-   ike -s', 'čeq',
            'čeq  -i', 'rekʼe']

    def test_repr(self):
    	assert "Original" and "Contents" in repr(self.toolbox_line)


class TestToolbox:

    def setup(self):
        self.filename = os.path.join(os.path.dirname(__file__), "..",
            "sample_files", "toolbox_graf", "toolbox.txt")
        self.toolbox = poioapi.io.toolbox.Toolbox(self.filename)

    def test_lines(self):
        lines = self.toolbox.lines()
        assert len(lines) == 2539

    def test_records(self):
        records = self.toolbox.records('ref')
        assert len(records) == 296
        assert self.toolbox.tiers == set([
            'ref', 'ge', 'id', 'ps', 'tx', 'dt', 'nt', 'rt', 'rf', 'ft', 'mb',
            'graid'])


class TestParser:
    """
    This class contain the test methods to the
    class io.toolbox.py.

    """

    def setup(self):
        self.filename = os.path.join(os.path.dirname(__file__), "..",
        	"sample_files", "toolbox_graf", "toolbox.txt")
        self.parser = poioapi.io.toolbox.Parser(self.filename)
        self.parser.record_marker = "ref"
        self.parser.parse()

    def test_get_root_tiers(self):
        root_tiers = self.parser.get_root_tiers()
        assert len(root_tiers) == 1

    def test_get_child_tiers_for_tier(self):
        root_tiers = self.parser.get_root_tiers()
        child_tiers = self.parser.get_child_tiers_for_tier(root_tiers[0])

        assert len(child_tiers) == 11

    def test_get_annotations_for_tier(self):
        root_tiers = self.parser.get_root_tiers()
        root_annotations = self.parser.get_annotations_for_tier(root_tiers[0])

        assert len(root_annotations) == 295

        tier = poioapi.io.graf.Tier("mb")
        annoation_parent = root_annotations[0]

        tier_annotations = self.parser.get_annotations_for_tier(tier, annoation_parent)

        assert len(tier_annotations) == 8
