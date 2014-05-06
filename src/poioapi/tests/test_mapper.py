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


class TestAnnotationMapper:

    _am = None
    _sample_files = ''

    def setup(self):
        self._sample_file = os.path.join(os.path.dirname(__file__), "sample_files", "mapper", "example.json")

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