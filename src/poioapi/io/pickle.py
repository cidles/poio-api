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
import os
import sys
import collections

import poioapi.annotationtree
import poioapi.data
import poioapi.io.graf

# Set the type of string
if sys.version_info[:2] >= (3, 0):
    string_type = str
else:
    string_type = basestring


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
        self.data_hierarchy = self.annotation_tree.structure_type_handler.\
            data_hierarchy

        #self._tier_map = {}
        #self._find_structure_levels(self.data_hierarchy)

        self._annotations_for_parent = collections.defaultdict(list)
        self.last_used_id = 0
        for element in self.annotation_tree.tree:
            #self._get_elements_for_tier(element)
            self._build_indices(element, self.data_hierarchy)

    def get_root_tiers(self):
        return [poioapi.io.graf.Tier(self.data_hierarchy[0])]

    def get_child_tiers_for_tier(self, tier):
        return [poioapi.io.graf.Tier(t)
            for t in self.annotation_tree.structure_type_handler.\
                get_children_of_type(tier.name)]

    def get_annotations_for_tier(self, tier, annotation_parent=None):
        parent_id = None
        if annotation_parent:
            parent_id = annotation_parent.id
        return [poioapi.io.graf.Annotation(
            "a{0}".format(i['id']), i['annotation'])
                for i in self._annotations_for_parent[
                    (parent_id, tier.name)]]

    # TODO: fix stuff with regions, does not work right now
    def tier_has_regions(self, tier):
#        if 'region' in self._tier_map[tier.name]['values'][0]:
#            return True

        return False

    def region_for_annotation(self, annotation):
 #       for key, values in self._tier_map.items():
 #           for value in values['values']:
 #               if annotation.id == "a{0}".format(value['id']):
 #                   return value['region']

        return None

    def get_primary_data(self):
        """This method gets the information about
        the source data file.

        Returns
        -------
        primary_data : object
            PrimaryData object.

        """

        primary_data = poioapi.io.graf.PrimaryData()
        primary_data.type = primary_data.NONE
        primary_data.filename = "unknown"

        return primary_data

    def _build_indices(self, elements, hierarchy, parent = None):
        new_parent = None
        local_parent = None
        for i, t in enumerate(hierarchy):
            if isinstance(t, list):
                elements_list = elements[i]
                for e in elements_list:
                    if new_parent:
                        self._build_indices(e, t, new_parent)
                    else:
                        self._build_indices(e, t, parent)
            else:
                # workaround for ids that were written wrong to pickle file
                if elements[i]['id'] == '[':
                    elements[i]['id'] = self.last_used_id
                    self.last_used_id += 1

                if local_parent:
                    self._annotations_for_parent[(local_parent, t)].\
                        append(elements[i])
                else:
                    self._annotations_for_parent[(parent, t)].\
                        append(elements[i])
                new_parent = "a{0}".format(elements[i]['id'])
                if t == self.data_hierarchy[0]:
                    local_parent = new_parent

