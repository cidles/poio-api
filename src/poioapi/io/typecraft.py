# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

"""This module contains classes to access to
Typecraf files and generate GrAF files.
"""

from __future__ import absolute_import

import re

import xml.etree.ElementTree as ET

import poioapi.io.graf

class Parser(poioapi.io.graf.BaseParser):
    """
    Class that will handle the parse of
    Typecraft files.

    """

    def __init__(self, filepath):
        """Class's constructor.

        Parameters
        ----------
        filepath : str
            Path of the elan file.

        """

        self.filepath = filepath

        self.annotations_list = []

        self.parse()

    def parse(self):

        self.tree = ET.parse(self.filepath).getroot()

        self.xml_namespace = re.search('\{(.*)\}', self.tree.tag).group()

        texts = self.get_root_tiers("text")
        phrases = self.get_root_tiers("phrase")

        root_tiers = texts + phrases

        self.dependencies_map = dict()
        self.dependencies_map['text'] = {'parent':None, 'last_id':None, 'id':None}
        self.dependencies_map['phrase'] = {'parent':None, 'last_id':None, 'id':None}
        self.dependencies_map['word'] = {'parent':'phrase', 'last_id':1, 'id':1}
        self.dependencies_map['morpheme'] = {'parent':'word', 'last_id':1, 'id':1}
        self.dependencies_map['gloss'] = {'parent':'morpheme', 'last_id':1, 'id':1}
        self.dependencies_map['globaltags'] = {'parent':'phrase', 'last_id':1, 'id':1}

        if len(texts) > 0:
            self.dependencies_map['phrase']['parent'] = 'text'

        for root_tier in root_tiers:
            annotations = self.get_annotations_for_tier(root_tier)

            self.add_elements_to_annotation_list(root_tier, annotations)
            self.find_children_tiers_for_tier(root_tier)

    def get_root_tiers(self, tiers=None):

        root_tiers = self.tree.findall(self.xml_namespace+tiers)

        return root_tiers

    def get_child_tiers_for_tier(self, tier):

        tier_childs = []

        for child in tier:
            if len(child) > 0:
                tier_childs.append(child)
            elif child.tag == self.xml_namespace+"gloss" \
            or child.tag == self.xml_namespace+"globaltags" \
            or child.tag == self.xml_namespace+"morpheme":
                tier_childs.append(child)

        return tier_childs

    def get_annotations_for_tier(self, tier, annotation_parent=None):

        tier_annotations = []

        for annotation in tier:
            if len(annotation) is 0:
                tier_annotations.append(annotation)

        return tier_annotations

    def find_children_tiers_for_tier(self, tier):

        children = self.get_child_tiers_for_tier(tier)

        for child in children:
            annotations = self.get_annotations_for_tier(child)

            self.add_elements_to_annotation_list(child, annotations)

            child_children = self.get_child_tiers_for_tier(child)

            if len(child_children) > 0:
                self.find_children_tiers_for_tier(child)

    def add_elements_to_annotation_list(self, tier, annotations):

        features = {}

        for annotation in annotations:
            key = str(annotation.tag).replace(self.xml_namespace, '')
            value = annotation.text

            if key != 'gloss' and key[1] != "globaltags":
                features[key] = value

        # Get the rest of the annotation information
        for attribute in tier.attrib:
            features[attribute] = tier.attrib[attribute]

        if tier.tag == self.xml_namespace+"gloss":
            features['annotation_value'] = tier.text

        annotation_name = str(tier.tag).replace(self.xml_namespace, '')
        parent_ref = self.dependencies_map[annotation_name]['parent']

        if self.dependencies_map[annotation_name]['parent'] is not None:
            annotation_ref = self.dependencies_map[annotation_name]['parent']+\
                             "/n" + str(self.dependencies_map[parent_ref]['last_id'])
        else:
            annotation_ref = None

        # Get and update indexes
        if annotation_name == "phrase" or annotation_name == "text":
            self.dependencies_map[annotation_name]['last_id'] =\
            self.dependencies_map[annotation_name]['id']
            self.dependencies_map[annotation_name]['last_id'] = features['id']

            index_number = features['id']
        else:
            index_number = str(self.dependencies_map[annotation_name]['id'])

            self.dependencies_map[annotation_name]['last_id'] = \
            self.dependencies_map[annotation_name]['id']
            self.dependencies_map[annotation_name]['id']+=1

        annotation_id = annotation_name + "/a" + index_number

        self.annotations_list.append({'parent_ref':parent_ref,
                                      'annotation_name':annotation_name,
                                      'annotation_ref':annotation_ref,
                                      'annotation_id':annotation_id,
                                      'index_number':index_number,
                                      'prefix_name':annotation_name,
                                      'regions':None,
                                      'features':features})

    def region_for_annotation(self, annotation):
        pass

    def tier_has_regions(self, tier):
        pass