# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

"""This module contains classes to access
excel data.

"""

from __future__ import absolute_import

import csv
import codecs

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

        with codecs.open(self.filepath, 'r', 'utf-8') as csvfile:
            rows = csv.reader(csvfile, delimiter='|')

            i = 0
            cycle = 0
            words_row = None

            for row in rows:
                if i is 1:
                    words_row = row
                elif i is 4:
                    self._get_columns_in_rows(words_row, 1, cycle)
                    self._get_columns_in_rows(row, i, cycle)
                else:
                    self._get_columns_in_rows(row, i, cycle)

                if i == 7:
                    i = 0
                    cycle += 1
                else:
                    i += 1

    def _get_columns_in_rows(self, row, i, cycle):
        for j, column in enumerate(row):
            if column:
                if i == 2:
                    self.clause_ids[j] = column
                else:
                    id = self._next_id(i, j)

                    if i is 1:
                        index = 3
                    elif i is 3:
                        index = 0
                    elif i is 4:
                        index = 1
                    elif i >= 5:
                        index = 4
                    else:
                        index = i - 1

                    parent = self._find_parent_id(index, j, cycle)

                    self.list_map[i].append({'id': id, 'value': column,
                                             'position': j, 'parent': parent,
                                             'cycle': cycle})

    def _find_parent_id(self, index, position, cycle):
        if index < 0:
            return None
        else:
            last_position = 0
            last_element = None
            filter_list = [e for e in self.list_map[index]
                           if e['cycle'] == cycle]

            for i, element in enumerate(filter_list):
                if position in range(last_position, element['position']):
                    if last_element is None:
                        return element['id']
                    else:
                        return last_element['id']

                if i == len(filter_list) - 1:
                    return element['id']

                last_position = element['position']
                last_element = element

    def _next_id(self, i=0, j=0):
        if i == 3:
            return self.clause_ids[j] # clause_types ids
        else:
            current_id = self._current_id + 1
            self._current_id = current_id

        return str(current_id)

    def get_root_tiers(self):
        return [poioapi.io.graf.Tier('ref')]

    def get_child_tiers_for_tier(self, tier):
        if tier.name == 'ref':
            return [poioapi.io.graf.Tier('clause_type')]

        elif tier.name == 'clause_type':
            return [poioapi.io.graf.Tier('word')]

        elif tier.name == 'word':
            return [poioapi.io.graf.Tier('grammatical_relation')]

        elif tier.name == 'grammatical_relation':
            return [poioapi.io.graf.Tier('part_of_spech')] +\
                   [poioapi.io.graf.Tier('translation')] +\
                   [poioapi.io.graf.Tier('reference_tracking')]

        return None

    def get_annotations_for_tier(self, tier, annotation_parent=None):
        annotations = []

        if tier.name == "ref":
            return [poioapi.io.graf.Annotation(tier['id'], tier['value'])
                    for tier in self.list_map[0]]

        elif tier.name == 'clause_type':
            annotations = self._get_annotations_from_list(3,
                annotation_parent.id)

        elif tier.name == 'word':
            annotations = self._get_annotations_from_list(1,
                annotation_parent.id)

        elif tier.name == 'grammatical_relation':
            annotations = self._get_annotations_from_list(4,
                annotation_parent.id)

        elif tier.name == 'part_of_spech':
            annotations = self._get_annotations_from_list(5,
                annotation_parent.id)

        elif tier.name == 'translation':
            annotations = self._get_annotations_from_list(6,
                annotation_parent.id)

        elif tier.name == 'reference_tracking':
            annotations = self._get_annotations_from_list(7,
                annotation_parent.id)

        return annotations

    def _get_annotations_from_list(self, i, parent_id):
        annotations = []

        for tier in self.list_map[i]:
            if tier['parent'] == parent_id:
                annotations.append(poioapi.io.graf.
                Annotation(tier['id'], tier['value']))

        return annotations

    def tier_has_regions(self, tier):
        pass

    def region_for_annotation(self, annotation):
        pass