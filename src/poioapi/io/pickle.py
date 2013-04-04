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

        self.filepath = filepath

#        self.parse()

    def parse(self):

        self.annotation_tree = poioapi.annotationtree.AnnotationTree(poioapi.data.GRAID)
        self.data_hierarchy = self.annotation_tree.structure_type_handler.data_hierarchy

        self.annotation_tree.load_tree_from_pickle(self.filepath)

#        print(self.annotation_tree.tree)

        #
        #        for index, element in enumerate(self.annotation_tree.elements()):
        #            print(index, element[0])
        #
        #        pass

#        print(self.data_hierarchy)
        root_tiers = self.get_root_tiers()

        firs_tier = root_tiers[0]

#        print(root_tiers)




        tiers = self.get_child_tiers_for_tier(firs_tier)

#        for tier in tiers:
#            print(tier.name)

        clause_unit = tiers[0]

        clause_tiers = self.get_child_tiers_for_tier(clause_unit)

#        for tier in clause_tiers:
#            print(tier.name)

#        print(self.annotation_tree.tree[0])

        self.hierarchy_level_list = {}

        self._find_hiearchy_levels(self.data_hierarchy)

        tier = poioapi.io.graf.Tier('clause_unit')

        annotations = self.get_annotations_for_tier(tier)

        for annotation in annotations:
            print(annotation.id, annotation.value)

    def get_root_tiers(self):
        return [poioapi.io.graf.Tier(self.data_hierarchy[0])]

    def get_child_tiers_for_tier(self, tier):
        return [poioapi.io.graf.Tier(tier) for tier in
                self._find_tier_in_structure(tier, self.data_hierarchy)]

    def get_annotations_for_tier(self, tier, annotation_parent=None):
        self._tier_annotations = []

        for element in self.annotation_tree.tree:
            self.aaa(tier, element)

        return [poioapi.io.graf.Annotation(i['id'],
            i['annotation']) for i in self._tier_annotations]

    def aaa(self, tier, elements, level = 0):
        for position, element in enumerate(elements):
            if isinstance(element, list):
                self.aaa(tier, element, level + 1)
            else:
                print(tier.name)
                print(level)
                print(position)
                if position == self.hierarchy_level_list[tier.name]['position']\
                and level == self.hierarchy_level_list[tier.name]['level']:
                    self._tier_annotations.append(element)

    def tier_has_regions(self, tier):
        pass

    def region_for_annotation(self, annotation):
        pass

    def _find_hiearchy_levels(self, data_hierarchy, level = 0):
        for position, element in enumerate(data_hierarchy):
            if isinstance(element, list):
                self._find_hiearchy_levels(element, (level + 1))
            else:
                self.hierarchy_level_list[element] = {'level':level,
                                                      'position':position}

    def _find_tier_in_structure(self, tier, structure):
        for element in structure:
            if isinstance(element, list):
                aux = self._find_tier_in_structure(tier, element)
                if aux is not None:
                    return aux
            else:
                if element == tier.name:
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
