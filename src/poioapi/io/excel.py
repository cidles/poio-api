# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

import csv

import poioapi.io.graf

class Parser(poioapi.io.graf.BaseParser):

    def __init__(self, filepath):
        """Class's constructor.

        Parameters
        ----------
        filepath : str
            Path of the elan file.

        """

        self.filepath = filepath

        self.parse()

    def parse(self):
        self.list_map = {0: [], 1: [], 2: [], 3: [],
                         4: [], 5: [], 6: [], 7: []}

        self._current_id = 0
        self.current_parent = None

        with open(self.filepath, 'rb') as csvfile:
            excel = csv.reader(csvfile, delimiter='|')

            i = 0
            for row in excel:
                for j, column in enumerate(row):
                    if column:
                        self.list_map[i].append({'id':self._next_id(i), 'value':column,
                                                 'i':i, 'j':j})
                if i == 7:
                    i = 0
                else:
                    i += 1

    def _next_id(self, i):

        if i == 2 or i == 3:
            return 0
        else:
            current_id = self._current_id + 1
            self._current_id = current_id

        return current_id

    def _get_clause_id(self):
        return None

    def get_root_tiers(self):

        return [poioapi.io.graf.Tier(tier['value'], 'ref')
                for tier in self.list_map[0]]

    def get_annotations_for_tier(self, tier, annotation_parent=None):
        pass

    def get_child_tiers_for_tier(self, tier):
        if tier.linguistic_type == 'ref':
            return [poioapi.io.graf.Tier(tier['value'], 'clause_type')
                    for tier in self.list_map[3]]

        elif tier.linguistic_type == 'clause_type':
            return [poioapi.io.graf.Tier(tier['value'], 'word')
                    for tier in self.list_map[1]]

        elif tier.linguistic_type == 'word':
            return [poioapi.io.graf.Tier(tier['value'],
                'grammatical_relation') for tier in self.list_map[4]]

        elif tier.linguistic_type == 'grammatical_relation':
            parts_of_spech = [poioapi.io.graf.Tier(tier['value'],
                'part_of_spech') for tier in self.list_map[5]]

            translations = [poioapi.io.graf.Tier(tier['value'],
                'translation') for tier in self.list_map[6]]

            reference_trackings = [poioapi.io.graf.Tier(tier['value'],
                'reference_tracking') for tier in self.list_map[7]]

            return parts_of_spech + translations + reference_trackings

        return None

    def tier_has_regions(self, tier):
        pass

    def region_for_annotation(self, annotation):
        pass