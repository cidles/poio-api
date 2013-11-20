# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

import os
import tempfile
import difflib

import poioapi.io.tcf
import poioapi.io.elan
import poioapi.io.graf


class TestParser:
    """
    This class contain the test methods to the
    class io.tcf.py.

    """

    def setup(self):
        self.filename = os.path.join(os.path.dirname(__file__), "..", "sample_files",
            "tcf_graf", "corpus.xml")

        self.basedirname = os.path.dirname(self.filename)

        self.parser = poioapi.io.tcf.Parser(self.filename)

    def test_get_root_tiers(self):
        root_tiers = self.parser.get_root_tiers()

        assert len(root_tiers) == 1

    def test_get_child_tiers_for_tier(self):
        root_tiers = self.parser.get_root_tiers()
        root_child_tier = self.parser.get_child_tiers_for_tier(root_tiers[0])
        assert root_child_tier[0].name == "tokens"

        children_tier = self.parser.get_child_tiers_for_tier(root_child_tier[0])
        assert len(children_tier) == 2

    def test_get_annotations_for_tier(self):
        root_tiers = self.parser.get_root_tiers()
        root_annotations = self.parser.get_annotations_for_tier(root_tiers[0])
        assert len(root_annotations) == 2

        parent_annotation = poioapi.io.graf.Annotation("s1", "t1 t2 t3 t4 t5")
        token_tier = self.parser.get_child_tiers_for_tier(root_tiers[0])
        token_annotations = self.parser.get_annotations_for_tier(token_tier[0], parent_annotation)
        assert len(token_annotations) == 5

    def test_tier_has_regions(self):
        root_tiers = self.parser.get_root_tiers()
        assert self.parser.tier_has_regions(root_tiers[0])

    def test_region_for_annotation(self):
        root_tiers = self.parser.get_root_tiers()
        root_annotations = self.parser.get_annotations_for_tier(root_tiers[0])
        region = self.parser.region_for_annotation(root_annotations[0])
        assert region == ('1', '20')

class TestWriter:

    def setup(self):
        self.filename = os.path.join(os.path.dirname(__file__), "..", "sample_files",
            "elan_graf", "example.eaf")

        self.parser = poioapi.io.elan.Parser(self.filename)
        self.writer = poioapi.io.tcf.Writer()

    def test_write(self):
        outputfile = tempfile.TemporaryFile()
        self.converter = poioapi.io.graf.GrAFConverter(self.parser, self.writer)
        self.converter.parse()
        self.converter.write(outputfile)

        testfile = os.path.join(os.path.dirname(__file__), "..", "sample_files",
            "tcf_graf", "test_write.tcf")

        #outputfile2 = os.path.join(os.path.dirname(__file__), "..", "sample_files",
        #    "tcf_graf", "test_write.tcf")
        #self.converter.write(outputfile2)

        outputfile.seek(0)
        fromlines = outputfile.readlines()
        fromlines = [l.decode("utf-8") for l in fromlines]
        tolines = open(testfile, 'U').readlines()
 
        diff = difflib.unified_diff(fromlines, tolines)
        for line in diff:
            if not line.startswith("---") and not line.startswith("+++") and \
                    (line.startswith("+") or line.startswith("-")):
                assert "ed:phoneticsegmentation" in line
