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
            Path of the typecraft file.

        """

        self.filepath = filepath

        self.parse()

    def parse(self):
        self._position_tier_map = {}
        self.dependencies_map = dict()
        self.dependencies_map['word'] = {'parent': 'phrase', 'last_id': 1, 'id': 1}
        self.dependencies_map['morpheme'] = {'parent': 'word', 'last_id': 1, 'id': 1}
        self.dependencies_map['gloss'] = {'parent': 'morpheme', 'last_id': 1, 'id': 1}
        self.dependencies_map['globaltags'] = {'parent': 'phrase', 'last_id': 1, 'id': 1}
        self.dependencies_map['globaltag'] = {'parent': 'globaltags', 'last_id': 1, 'id': 1}

        self.tree = ET.parse(self.filepath).getroot()
        self.xml_namespace = re.search('\{(.*)\}', self.tree.tag).group()

    def get_root_tiers(self):
        text_tiers = [poioapi.io.graf.Tier(tier.attrib['id'], "text")
                      for tier in self.tree.findall(self.xml_namespace + "text")]

        phrase_tiers = [poioapi.io.graf.Tier(tier.attrib['id'], "phrase")
                        for tier in self.tree.findall(self.xml_namespace + "phrase")]

        return text_tiers + phrase_tiers

    def get_child_tiers_for_tier(self, tier):
        tiers = []

        if tier.name not in self._position_tier_map:
            self._position_tier_map[tier.name] = []

        if tier.linguistic_type == "text":
            return [poioapi.io.graf.Tier(child_tier.attrib['id'], "phrase")
                    for child_tier in self.tree.findall(self.xml_namespace + tier.linguistic_type +
                                                        "[@id='" + tier.name + "']/phrase")]
        elif tier.linguistic_type == "phrase":
            for (i, _) in enumerate(self.tree.findall(self.xml_namespace + tier.linguistic_type
                                                      + "[@id='" + tier.name + "']/"
                                                      + self.xml_namespace + "word")):
                name = "w" + str(self._next_id("word"))
                self._position_tier_map[tier.name].append({'name': name, 'position': i})
                tiers.append(poioapi.io.graf.Tier(name, "word"))

            for (i, _) in enumerate(self.tree.findall(self.xml_namespace + tier.linguistic_type
                                                      + "[@id='" + tier.name + "']/"
                                                      + self.xml_namespace + "globaltags")):
                name = "gts" + str(self._next_id("globaltags"))
                self._position_tier_map[tier.name].append({'name': name, 'position': i})
                tiers.append(poioapi.io.graf.Tier(name, "globaltags"))
        else:
            if tier.linguistic_type == "word":
                words = self._find_words(tier.name)

                for (i, _) in enumerate(words.findall(self.xml_namespace + "morpheme")):
                    name = "m" + str(self._next_id("morpheme"))
                    self._position_tier_map[tier.name].append({'name': name, 'position': i})
                    tiers.append(poioapi.io.graf.Tier(name, "morpheme"))

            elif tier.linguistic_type == "globaltags":
                globaltags = self._find_globaltags(tier.name)

                for (i, _) in enumerate(globaltags.findall(self.xml_namespace + "globaltag")):
                    name = "gt" + str(self._next_id("globaltag"))
                    self._position_tier_map[tier.name].append({'name': name, 'position': i})
                    tiers.append(poioapi.io.graf.Tier(name, "globaltag"))

            elif tier.linguistic_type == "morpheme":
                (word_name, morpheme_position) = self._find_tier_position(tier.name)

                words = self._find_words(word_name)

                morpheme = words.findall(self.xml_namespace + "morpheme")[morpheme_position]

                for (i, _) in enumerate(morpheme.findall(self.xml_namespace + "gloss")):
                    name = "g" + str(self._next_id("gloss"))
                    self._position_tier_map[tier.name].append({'name': name, 'position': i})
                    tiers.append(poioapi.io.graf.Tier(name, "gloss"))

        return tiers

    def get_annotations_for_tier(self, tier, annotation_parent=None):
        if tier.linguistic_type == "text" or tier.linguistic_type == "phrase":
            elements = self.tree.find(self.xml_namespace + tier.linguistic_type
                                         + "[@id='" + tier.name + "']")
        else:
            elements = self._get_tier_elements(tier)

        features = {}

        if tier.linguistic_type == "gloss":
            annotation_value = elements.text
        else:
            annotation_value = None

        for attribute in elements.attrib:
            features[attribute] = elements.attrib[attribute]

        for element in elements:
            if len(element) is 0:
                key = str(element.tag).replace(self.xml_namespace, '')

                if key != 'gloss' and key[1] != "globaltags":
                    features[key] = element.text

        return [poioapi.io.graf.Annotation(tier.name, annotation_value, features)]

    def _get_tier_elements(self, tier):
        (parent_name, tier_position) = self._find_tier_position(tier.name)

        if tier.linguistic_type == "word":
            elements = self.tree.findall(self.xml_namespace + "phrase[@id='"
                                         + parent_name + "']/" + self.xml_namespace
            + "word")[tier_position]

        if tier.linguistic_type == "globaltags":
            elements = self.tree.findall(self.xml_namespace + "phrase[@id='"
                                         + parent_name + "']/" + self.xml_namespace
            + "globaltags")[tier_position]

        elif tier.linguistic_type == "morpheme":
            words = self._find_words(parent_name)

            elements = words.findall(self.xml_namespace + "morpheme")[tier_position]

        elif tier.linguistic_type == "gloss":
            (morpheme_name, gloss_position) = self._find_tier_position(tier.name)
            (word_name, morpheme_position) = self._find_tier_position(morpheme_name)

            words = self._find_words(word_name)

            morphemes = words.findall(self.xml_namespace + "morpheme")[morpheme_position]
            elements = morphemes.findall(self.xml_namespace + "gloss")[gloss_position]

        return elements

    def _find_words(self, word_name):
        (phrase_name, word_position) = self._find_tier_position(word_name)

        words = self.tree.findall(self.xml_namespace + "phrase[@id='" + phrase_name + "']/" +
                                  self.xml_namespace + "word")[word_position]
        return words

    def _find_globaltags(self, globaltag_name):
        (phrase_name, globaltag_position) = self._find_tier_position(globaltag_name)

        globaltags = self.tree.findall(self.xml_namespace + "phrase[@id='" + phrase_name + "']/" +
                                  self.xml_namespace + "globaltags")[globaltag_position]
        return globaltags

    def _next_id(self, name):
        current_id = self.dependencies_map[name]['id']

        self.dependencies_map[name]['id'] = current_id + 1
        self.dependencies_map[name]['last_id'] = current_id

        return current_id

    def _find_tier_position(self, name):
        for key, values in self._position_tier_map.items():
            for value in values:
                if name == value['name']:
                    return key, value['position']

    def region_for_annotation(self, annotation):
        pass

    def tier_has_regions(self, tier):
        pass