# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2014 Poio Project
# Author: Pedro Manha <pmanha@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

# from __future__ import unicode_literals

import os

import poioapi.io.odin
import poioapi.io.graf
import poioapi.data
import poioapi.mapper


class TestParser:

    def __init__(self):
        self._samples_dir = os.path.join(os.path.dirname(__file__), '..',
            'sample_files', 'odin')
        self._inputfile = ''

        self._root_tier = None

        self._parser = None

    def setup(self):
        self._inputfile = os.path.join(self._samples_dir, 'odin_test.xml')
        self._parser = poioapi.io.odin.Parser(self._inputfile, None)

        self._root_tier = poioapi.io.graf.Tier(self._parser.tier_labels.tier_label(
            poioapi.data.TIER_UTTERANCE))

    def test_get_root_tiers(self):
        root_tiers = self._parser.get_root_tiers()
        assert len(root_tiers) == 1

    def test_get_child_tiers_for_tier(self):
        root_tiers = self._parser.get_root_tiers()

        child_tiers = self._parser.get_child_tiers_for_tier(root_tiers[0])
        assert len(child_tiers) == 2
        ct_name_list = [a.name for a in child_tiers]
        assert self._parser.tier_labels.tier_label(poioapi.data.TIER_WORD) in ct_name_list
        assert self._parser.tier_labels.tier_label(poioapi.data.TIER_TRANSLATION) in ct_name_list

        tier = poioapi.io.graf.Tier(poioapi.data.tier_labels[poioapi.data.TIER_WORD])
        child_tiers = self._parser.get_child_tiers_for_tier(tier)
        assert len(child_tiers) == 1
        assert child_tiers[0].name == self._parser.tier_labels.tier_label(
            poioapi.data.TIER_MORPHEME)

    def test_get_annotations_for_tier(self):
        root_tiers = self._parser.get_annotations_for_tier(self._root_tier)
        assert len(root_tiers) == 18

    def test_gloss_special_case(self):
        word_tier = poioapi.io.graf.Tier(self._parser.tier_labels.tier_label(
            poioapi.data.TIER_WORD))
        m_tier = poioapi.io.graf.Tier(self._parser.tier_labels.tier_label(
            poioapi.data.TIER_MORPHEME))
        g_tier = poioapi.io.graf.Tier(self._parser.tier_labels.tier_label(
            poioapi.data.TIER_GLOSS))

        root = self._parser.get_annotations_for_tier(self._root_tier)[0]
        words = self._parser.get_annotations_for_tier(word_tier, root)
        morphemes = []

        for w in words:
            morphemes.extend(self._parser.get_annotations_for_tier(m_tier, w))

        glosses = []
        for m in morphemes:
            glosses.extend(self._parser.get_annotations_for_tier(g_tier, m))

        assert len(glosses) == 7

        expected = ['the', 'Paulo', 'worked', 'more', 'than', 'what', 'nobody']
        assert set(expected) == set([a.value for a in glosses])