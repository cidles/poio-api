# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

""" This document contain the responsible
methods to write and parse the GrAF files
from a pickle file using Annotation Tree.
"""

from __future__ import absolute_import
import codecs
import os

import poioapi.annotationtree
import poioapi.data
import poioapi.io.graf

class Parser(poioapi.io.graf.BaseParser):
    """
    This class contain the methods to the
    write the GrAF files from pickle files.

    """

    def __init__(self, filepath):
        """Class's constructor.

        Parameters
        ----------
        filepath : str
            Path of the pickle file.

        """

        try:
            self.filepath = filepath.name
        except AttributeError as attributeError:
            self.filepath = filepath

        (self.basedirname, _) = os.path.splitext(os.path.abspath(self.filepath))

        self.parse()

    def parse(self):
        self.annotation_tree = poioapi.annotationtree.AnnotationTree()
        self.annotation_tree.load_tree_from_pickle(self.filepath)
        self.data_hierarchy = self.annotation_tree.structure_type_handler.data_hierarchy

        self._tier_map = {}
        self._find_structure_levels(self.data_hierarchy)

        for element in self.annotation_tree.tree:
            self._get_elements_for_tier(element)

        self._create_raw_file()

    def get_root_tiers(self):
        return [poioapi.io.graf.Tier(self.data_hierarchy[0])]

    def get_child_tiers_for_tier(self, tier):
        return [poioapi.io.graf.Tier(tier) for tier in
                self._find_tier_in_structure(tier, self.data_hierarchy)]

    def get_annotations_for_tier(self, tier, annotation_parent=None):
        if annotation_parent is not None:
            annotation_parent_id = annotation_parent.id
        else:
            annotation_parent_id = None

        return [poioapi.io.graf.Annotation(str(i['id']), i['annotation'])
                for i in self._tier_map[tier.name]['values']
                if i['annotation'] and i['parent'] == annotation_parent_id]

    def tier_has_regions(self, tier):
        if 'region' in self._tier_map[tier.name]['values'][0]:
            return True

        return False

    def region_for_annotation(self, annotation):
        for key, values in self._tier_map.items():
            for value in values['values']:
                if annotation.id == str(value['id']):
                    return value['region']

        return None

    def _get_elements_for_tier(self, elements, parent_element = None, level = 0):
        for position, element in enumerate(elements):
            if isinstance(element, list):
                if not isinstance(element[0], list):
                    level += 1

                self._get_elements_for_tier(element, parent_element, level)

                if position + 1 <= len(elements) - 1:
                    if isinstance(elements[position + 1], list):
                        level -= 1
            else:
                key = self._find_key_in_map(level, position)
                element['parent'] = parent_element
                self._tier_map[key]['values'].append(element)

                if position is 0:
                    parent_element = str(element['id'])

    def _find_key_in_map(self, level, position):
        for key, values in self._tier_map.items():
            if values['position'] == position \
            and values['level'] == level:
                return key

        return None

    def _find_structure_levels(self, data_hierarchy, level = 0):
        for position, element in enumerate(data_hierarchy):
            if isinstance(element, list):
                self._find_structure_levels(element, (level + 1))
            else:
                self._tier_map[element] = {'level':level, 'position':position,
                                           'values':[]}

    def _find_tier_in_structure(self, tier, structure):
        for i, element in enumerate(structure):
            if isinstance(element, list):
                aux = self._find_tier_in_structure(tier, element)
                if aux is not None:
                    return aux
                else:
                    return []
            else:
                if element == tier.name and i == 0:
                    return self._find_childs_from_structure(structure)

    def _find_childs_from_structure(self, structure):
        auxliar_strucutre = []

        for element in structure:
            if element == structure[0]:
                continue
            if isinstance(element, list):
                auxliar_strucutre.append(element[0])
            else:
                auxliar_strucutre.append(element)

        return auxliar_strucutre

    def _create_raw_file(self):
        """Creates an txt file with the data in the
        Annotation Tree file. Passing only the sentences.

        """

        file = os.path.abspath(self.basedirname + '.txt')
        f = codecs.open(file,'w', 'utf-8') # Need the encode

        # Verify the elements
        for element in self.annotation_tree.elements():

            # Get the utterance
            utterance = element[0]

            # Write the content to the txt file
            f.write(utterance.get('annotation') + '\n')

        # Close txt file
        f.close()
