# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT
import codecs

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
        self.clause_ids = {}

#        with open(self.filepath, 'rb') as csvfile: without the enonding Python 2.x
        with codecs.open(self.filepath, 'rb', "utf-8") as csvfile:
            excel = csv.reader(csvfile, delimiter='|')

            i = 0
            words_rows_list = []
            for row in excel:

                if i is 1:
                    words_rows_list.append(row)
                else:
                    self._get_columns_in_rows(row, i)

                if i == 7:
                    i = 0
                else:
                    i += 1

        for words_row in words_rows_list:
            self._get_columns_in_rows(words_row, 1)

    def _get_columns_in_rows(self, row, i):
        for j, column in enumerate(row):

            if column:
                parent = None

                if i == 2:
                    self.clause_ids[j] = column
                else:
                    id = self._next_id(i)

                    if i != 3 and i != 0:
                        parent = self._find_parent_id(i, j)

                    self.list_map[i].append({'id':id, 'value':column,
                                             'position':j, 'parent':parent})

    def _find_parent_id(self, i, j):

        for element in self.list_map[i-1]:
            if element['position'] == j:
                return element['id']

        return None

    def _next_id(self, i = 0, j = 0):

        if i == 3:
            return self.clause_ids[j]
        else:
            current_id = self._current_id + 1
            self._current_id = current_id

        return str(current_id)

    def get_root_tiers(self):

        return [poioapi.io.graf.Tier(tier['id'], 'ref')
                for tier in self.list_map[0]]

    def get_annotations_for_tier(self, tier, annotation_parent=None):

        if tier.linguistic_type == "ref":
            return [poioapi.io.graf.Annotation(self._next_id(), tier['value'])
                    for tier in self.list_map[0]]

#        elif tier.linguistic_type == 'clause_type':
#            print(tier.name)
#            for element in self.list_map.items():
#                key = element[0]
#                list_map = element[1]
#                for value in list_map:
#                    print(value['parent'])
#                    print(annotation_parent.id)
#                    if value['parent'] == annotation_parent.id:

#            return [poioapi.io.graf.Tier(tier['id'], 'word')
#                    for tier in self.list_map[1]]

        return []

    def get_child_tiers_for_tier(self, tier):
        if tier.linguistic_type == 'ref':
            return [poioapi.io.graf.Tier(tier['id'], 'clause_type')
                    for tier in self.list_map[3]]

        elif tier.linguistic_type == 'clause_type':
            return [poioapi.io.graf.Tier(tier['id'], 'word')
                    for tier in self.list_map[1]]

        elif tier.linguistic_type == 'word':
            return [poioapi.io.graf.Tier(tier['id'],
                'grammatical_relation') for tier in self.list_map[4]]

        elif tier.linguistic_type == 'grammatical_relation':
            parts_of_spech = [poioapi.io.graf.Tier(tier['id'],
                'part_of_spech') for tier in self.list_map[5]]

            translations = [poioapi.io.graf.Tier(tier['id'],
                'translation') for tier in self.list_map[6]]

            reference_trackings = [poioapi.io.graf.Tier(tier['id'],
                'reference_tracking') for tier in self.list_map[7]]

            return parts_of_spech + translations + reference_trackings

        return None

    def tier_has_regions(self, tier):
        pass

    def region_for_annotation(self, annotation):
        pass