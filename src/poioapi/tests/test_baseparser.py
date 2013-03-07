# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

import os
import re

import xml.etree.ElementTree as ET

from poioapi.io import graf

class TestBaseParser:

    def setup(self):
        self.filename = os.path.join(os.path.dirname(__file__), "sample_files",
            "elan_graf", "example.eaf")

        tree = ET.parse(self.filename)
        self.root = tree.getroot()

    def test_get_root_tiers(self):

        tiers = self.root.findall('TIER')

        root_tiers = []

        for tier in tiers:
            if not 'PARENT_REF' in tier.attrib:
                root_tiers.append(tier)

        assert(len(root_tiers) == 4)

    def test_get_child_tiers_for_tier(self):

        root_tier = "W-Spch"
        tier_childs = self.root.findall("TIER[@PARENT_REF='"+root_tier+"']")

        assert(len(tier_childs) == 2)

    def test_find_children_tiers_for_tier(self, tier):

        #children = self.get_child_tiers_for_tier(tier)

        #for child in children:
            #print("Parent: "+tier.attrib['TIER_ID'])
            #print("-->"+child.attrib['TIER_ID'])
            #child_children = self.get_child_tiers_for_tier(child)
            #if len(child_children) > 0:
                #self.get_child_tiers_for_child_tier(child)

        pass

    def test_get_annotations_for_tier(self):

        root_tier = "W-Spch"
        tier_annotations = self.root.findall("TIER[@TIER_ID='"+root_tier+"']/ANNOTATION")

        assert(len(tier_annotations) == 15)