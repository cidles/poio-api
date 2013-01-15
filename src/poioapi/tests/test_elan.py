# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

import os

from poioapi import data
from poioapi.io import elan

class TestElan:

    def test_find_hierarchy_parents(self):
        data_structure = ['utterance',['clause',['word']],'translation']

        filename = os.path.join(os.path.dirname(__file__), "sample_files",
            "balochi_graf", "balochi.hdr")

        elan_object = elan.Elan(filename, data.DataStructureTypeWithConstraints)

        expected_result = {'clause': 'utterance',
                           'translation': 'utterance',
                           'utterance': None,
                           'word': 'clause'}

        elan_object._find_hierarchy_parents(data_structure, None)

        final_result = elan_object.data_hierarchy_parent_dict

        assert(final_result == expected_result)