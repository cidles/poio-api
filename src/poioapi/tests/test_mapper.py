# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: Peter Bouda <pbouda@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

import os.path
import filecmp

import poioapi.mapper
import poioapi.data


class TestTierMapper:

    _tm = None
    _sample_file = ''

    def setup(self):
        self._sample_file = os.path.join(os.path.dirname(__file__),
                                         'sample_files', 'mapper',
                                         'example.json')

    def test_load_mapping(self):
        self._tm = poioapi.mapper.TierMapper()
        self._tm.load_mapping(self._sample_file)

        assert len(self._tm._tier_mapping) == 2

        gloss_tier_labels = self._tm.tier_labels(poioapi.data.TIER_GLOSS)
        pos_tier_labels = self._tm.tier_labels(poioapi.data.TIER_POS)

        assert len(gloss_tier_labels) == 1
        assert len(pos_tier_labels) == 1

    def test_tier_labels(self):
        self._tm = poioapi.mapper.TierMapper()
        self._tm.load_mapping(self._sample_file)

        tiers_to_succeed = ['gloss']
        tiers_to_test = self._tm.tier_labels(poioapi.data.TIER_GLOSS)

        assert set(tiers_to_succeed) == set(tiers_to_test)

        no_tier_type = []
        no_type_to_test = self._tm.tier_labels(poioapi.data.TIER_TRANSLATION)

        assert no_tier_type == no_type_to_test

    def test_tier_label(self):
        self._tm = poioapi.mapper.TierMapper()
        self._tm.load_mapping(self._sample_file)

        tier_to_succeed = 'pos'
        tier_to_test = self._tm.tier_label(poioapi.data.TIER_POS, 0)

        assert tier_to_succeed == tier_to_test

    def test_append(self):
        self._tm = poioapi.mapper.TierMapper()
        self._tm.load_mapping(self._sample_file)

        expected = ['gloss', 'test']
        self._tm.append_to_tier_labels(poioapi.data.TIER_GLOSS, ['test'])
        to_test = self._tm.tier_labels(poioapi.data.TIER_GLOSS)

        assert expected == to_test

    def test_exists(self):
        self._tm = poioapi.mapper.TierMapper()
        self._tm.load_mapping(self._sample_file)
        tag_exists = self._tm.tier_label_exists('pos')
        tag_not_exists = self._tm.tier_label_exists('test')

        assert tag_exists is True
        assert tag_not_exists is False



class TestAnnotationMapper:

    _am = None
    _sample_file = ''

    def setup(self):
        self._sample_file = os.path.join(os.path.dirname(__file__),
                                         "sample_files", "mapper",
                                         "example.json")

    def test_load_default(self):
        self._am = poioapi.mapper.AnnotationMapper(poioapi.data.MANDINKA, poioapi.data.TYPECRAFT)
        assert(len(self._am.annotation_mappings) == 1)
        assert(len(self._am.annotation_mappings[poioapi.data.TIER_GLOSS]) == 63)

    def test_load_user_mapping(self):
        self._am = poioapi.mapper.AnnotationMapper(poioapi.data.MANDINKA, poioapi.data.TYPECRAFT)
        self._am.load_mappings(self._sample_file)

        assert(len(self._am.annotation_mappings[poioapi.data.TIER_GLOSS]) == 65)

    def test_validate_tag(self):
        tag_to_succeed = '1SG'
        multitag_to_succeed = 'TAG'

        self._am = poioapi.mapper.AnnotationMapper(poioapi.data.MANDINKA, poioapi.data.TYPECRAFT)
        self._am.load_mappings(self._sample_file)

        assert(self._am.validate_tag(poioapi.data.TIER_GLOSS, tag_to_succeed) == '1SG')
        assert(self._am.validate_tag(poioapi.data.TIER_GLOSS, multitag_to_succeed) == 'TEST')

    def test_export(self):
        self._am = poioapi.mapper.AnnotationMapper(poioapi.data.MANDINKA, poioapi.data.TYPECRAFT)
        self._am.load_mappings(self._sample_file)

        self._am.add_to_missing(poioapi.data.TIER_GLOSS, '3PL')
        self._am.add_to_missing(poioapi.data.TIER_GLOSS, '4PL')
        filename = os.path.join(os.path.dirname(__file__), 'sample_files', 'mapper', 'example_export_test.json')
        expected_filename = os.path.join(os.path.dirname(__file__), 'sample_files', 'mapper', 'example_export.json')
        self._am.export_missing_tags(filename)

        assert(os.path.getsize(filename) == os.path.getsize(expected_filename))
        assert(filecmp.cmp(filename, expected_filename, False) is True)