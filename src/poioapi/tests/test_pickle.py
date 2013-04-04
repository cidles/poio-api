# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

import poioapi.io.pickle
import poioapi.io.graf

class TestPickle:

    def setup(self):
        self.data_structure = ['utterance',
            ['clause_unit',
                ['word', 'wfw', 'graid1'],
             'graid2'], 'translation', 'comment']

        self.pickle_parser = poioapi.io.pickle.Parser(None)

    def test_find_childs_in_hierarchy(self):
        utterance_childs = ['clause_unit', 'translation', 'comment']

        clause_unit = ['clause_unit',
            ['word', 'wfw', 'graid1'],
                       'graid2']
        clause_unit_childs = ['word', 'graid2']

        word = ['word', 'wfw', 'graid1']
        word_childs = ['wfw', 'graid1']

        utterance_strct = self.pickle_parser._find_childs_from_structure(self.data_structure)
        assert utterance_strct == utterance_childs

        clause_unit_strct = self.pickle_parser._find_childs_from_structure(clause_unit)
        assert clause_unit_strct == clause_unit_childs

        word_strct = self.pickle_parser._find_childs_from_structure(word)
        assert word_strct == word_childs

    def test_get_child_tiers_for_tier(self):

        tier = poioapi.io.graf.Tier('utterance')
        expected_child_tiers = ['clause_unit', 'translation', 'comment']

        assert self.pickle_parser._find_tier_in_structure(tier, self.data_structure) == \
               expected_child_tiers

        tier = poioapi.io.graf.Tier('clause_unit')
        expected_child_tiers = ['word', 'graid2']

        assert self.pickle_parser._find_tier_in_structure(tier, self.data_structure) == \
               expected_child_tiers