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
import sys

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

        with self.filepath as csvfile:
            rows = csv.reader(csvfile, delimiter="|", quotechar=None, doublequote=False)

            i = 0
            cycle = 0
            words_row = None

            for row in rows:
                row = self._decode_row(row)

                if i is 1:
                    self._empty_clause = self._next_id()
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

    def _decode_row(self, row):
        if sys.version_info[:2] < (3, 0):
            return [r.decode('utf-8') for r in row]

        return row

    def _get_columns_in_rows(self, row, i, cycle):
        for j, column in enumerate(row):
            if ";" in column and j == len(row) - 1:
                continue
            elif column and column != ";;":
                if i is 1 or i is 3:
                    index = 2
                elif i >= 4:
                    index = 1
                else:
                    index = None

                if i is 2:
                    id = column
                    index = 0
                else:
                    id = self._next_id()

                if index is None:
                    parent = None
                    self._ref_id = id
                else:
                    parent = self._find_parent_id(index, i, j, cycle)

                self._add_element_list_map(i, id, column, j, parent, cycle)

    def _find_parent_id(self, index, i, position, cycle):
        last_element = {'position':0}
        filter_list = [e for e in self.list_map[index]
                       if e['cycle'] == cycle]

        for f, element in enumerate(filter_list):
            if i == 2:
                return element['id']

            if i == 1:
                if position <= element['position']:
                    if position >= last_element['position']:
                        if 'id' in last_element and position != element['position']:
                            return last_element['id']
                        else:
                            return element['id']

                last_element = element

                if f == len(filter_list) - 1:
                    return last_element['id']

            elif position == element['position']:
                return element['id']

        parent = None
        last_element = {'position':0}

        for e in filter_list:
            if position <= e['position']:
                if position >= last_element['position']:
                    parent = e['parent']

            last_element = e

        if parent is not None or i is 1:
            if i == 1:
                parent = self._ref_id

            parent_id = self._next_id()

            self._add_element_list_map(index, parent_id, 'empty_value',
                position, parent, cycle)

            return parent_id

    def _add_element_list_map(self, index, id, value, position, parent, cycle):
        self.list_map[index].append({'id': id,
                                     'value': value,
                                     'position': position,
                                     'parent': parent,
                                     'cycle': cycle})

    def _next_id(self):
        current_id = self._current_id + 1
        self._current_id = current_id

        return str(current_id)

    def get_root_tiers(self):
        return [poioapi.io.graf.Tier('ref')]

    def get_child_tiers_for_tier(self, tier):
        if tier.name == 'ref':
            return [poioapi.io.graf.Tier('clause_id')]

        elif tier.name == 'clause_id':
            return [poioapi.io.graf.Tier('clause_type'),
                    poioapi.io.graf.Tier('word')]

        elif tier.name == 'word':
            return [poioapi.io.graf.Tier('grammatical_relation'),
                    poioapi.io.graf.Tier('part_of_spech'),
                    poioapi.io.graf.Tier('translation'),
                    poioapi.io.graf.Tier('reference_tracking')]

        return None

    def get_annotations_for_tier(self, tier, annotation_parent=None):
        annotations = []

        if tier.name == "ref":
            return [poioapi.io.graf.Annotation(tier['id'], tier['value'])
                    for tier in self.list_map[0]]

        elif tier.name == 'word':
            annotations = self._get_annotations_from_list(1,
                annotation_parent.id)

        elif tier.name == 'clause_id':
            annotations = self._get_annotations_from_list(2,
                annotation_parent.id)

        elif tier.name == 'clause_type':
            annotations = self._get_annotations_from_list(3,
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