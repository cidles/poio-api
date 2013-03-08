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

    def test_get_annotations_for_tier(self):

        root_tier = "W-Spch"
        tier_annotations = self.root.findall("TIER[@TIER_ID='"+root_tier+"']/ANNOTATION")

        assert(len(tier_annotations) == 15)

    def test_create_data_structure(self):

        depends_on_dict = dict()

        structure_elements = ['utterance','words','part_of_speech']

        parent = '_parent_linguistic_type_ref'
        son = '_linguistic_type_ref'

        if parent in depends_on_dict:
            if son not in depends_on_dict[parent]:
                depends_on_dict[parent].append(son)
        else:
            depends_on_dict[parent] = [son]

        pass