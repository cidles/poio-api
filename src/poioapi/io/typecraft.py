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
        self.tree = ET.parse(self.filepath).getroot()
        self.namespace = {'xmlns': re.findall(r"\{(.*?)\}", self.tree.tag)[0]}
        self._tier_information = dict()

    def get_root_tiers(self):
        text_tiers = [poioapi.io.graf.Tier(tier.attrib['id'], "text")
                      for tier in self.tree.findall("xmlns:text", self.namespace)]

        phrase_tiers = [poioapi.io.graf.Tier(tier.attrib['id'], "phrase")
                        for tier in self.tree.findall("xmlns:phrase", self.namespace)]

        return text_tiers + phrase_tiers

    def get_child_tiers_for_tier(self, tier):
        tiers = []

        if tier.linguistic_type == "text":
            return [poioapi.io.graf.Tier(child_tier.attrib['id'], "text")
                    for child_tier in self.tree.findall("xmlns:text[@id='" + tier.name +
                                                        "']/xmlns:phrase", self.namespace)]
        elif tier.linguistic_type == "phrase":
            for (i, _) in enumerate(self.tree.findall("xmlns:phrase[@id='" + tier.name
            + "']/xmlns:word", self.namespace)):
                tiers.append(poioapi.io.graf.Tier(self._add_child_tier(tier.name,
                    "word", i), "word"))

            for (i, _) in enumerate(self.tree.findall("xmlns:phrase[@id='" + tier.name
            + "']/xmlns:globaltags", self.namespace)):
                tiers.append(poioapi.io.graf.Tier(self._add_child_tier(tier.name,
                    "globaltags", i), "globaltags"))
        else:
            if tier.linguistic_type == "word":
                words = self._find_words(tier.name)

                for (i, _) in enumerate(words.findall("xmlns:morpheme", self.namespace)):
                    tiers.append(poioapi.io.graf.Tier(self._add_child_tier(tier.name,
                        "morpheme", i), "morpheme"))

            elif tier.linguistic_type == "globaltags":
                globaltags = self._find_globaltags(tier.name)

                for (i, _) in enumerate(globaltags.findall("xmlns:globaltag", self.namespace)):
                    tiers.append(poioapi.io.graf.Tier(self._add_child_tier(tier.name,
                        "globaltag", i), "globaltag"))

            elif tier.linguistic_type == "morpheme":
                (word_name, morpheme_position) = self._find_child_position(tier.name,
                    tier.linguistic_type)

                words = self._find_words(word_name)

                morpheme = words.findall("xmlns:morpheme", self.namespace)[morpheme_position]

                for (i, _) in enumerate(morpheme.findall("xmlns:gloss", self.namespace)):
                    tiers.append(poioapi.io.graf.Tier(self._add_child_tier(tier.name,
                        "gloss", i), "gloss"))
        return tiers

    def get_annotations_for_tier(self, tier, annotation_parent=None):
        if tier.linguistic_type == "text" or tier.linguistic_type == "phrase":
            elements = self.tree.find("xmlns:" + tier.linguistic_type +
                                      "[@id='" + tier.name + "']", self.namespace)
        else:
            elements = self._get_tier_elements(tier)

        features = {}

        if tier.linguistic_type == "gloss":
            annotation_value = elements.text
        else:
            annotation_value = None

        for attribute in elements.attrib:
            features[attribute] = elements.attrib[attribute]

        _namespace = re.search('\{(.*)\}', self.tree.tag).group()

        for element in elements:
            if len(element) is 0:
                key = str(element.tag).replace(_namespace, '')

                if key != "gloss" and key != "globaltags" and key != "morpheme":
                    features[key] = element.text

        return [poioapi.io.graf.Annotation(tier.name, annotation_value, features)]

    def _get_tier_elements(self, tier):
        (parent_id, tier_position) = self._find_child_position(tier.name, tier.linguistic_type)

        if tier.linguistic_type == "word":
            elements = self.tree.findall("xmlns:phrase[@id='" + parent_id + "']/xmlns:word",
                self.namespace)[tier_position]

        if tier.linguistic_type == "globaltags":
            elements = self.tree.findall("xmlns:phrase[@id='" + parent_id + "']/xmlns:globaltags",
                self.namespace)[tier_position]

        elif tier.linguistic_type == "morpheme":
            words = self._find_words(parent_id)

            elements = words.findall("xmlns:morpheme", self.namespace)[tier_position]

        elif tier.linguistic_type == "gloss":
            (morpheme_name, gloss_position) = self._find_child_position(tier.name, "gloss")
            (word_name, morpheme_position) = self._find_child_position(morpheme_name, "morpheme")

            words = self._find_words(word_name)

            morphemes = words.findall("xmlns:morpheme", self.namespace)[morpheme_position]
            elements = morphemes.findall("xmlns:gloss", self.namespace)[gloss_position]

        return elements

    def _add_child_tier(self, tier_name, linguistic_type, position):
        if linguistic_type not in self._tier_information:
            self._tier_information[linguistic_type] = {'last_id': 1,
                                                       'id': 1, 'childs': []}

        name = str(self._next_id(linguistic_type))

        self._tier_information[linguistic_type]['childs']\
        .append({'id': name, 'parent_id': tier_name, 'position': position})

        return name

    def _find_words(self, word_name):
        (phrase_name, word_position) = self._find_child_position(word_name, "word")

        words = self.tree.findall("xmlns:phrase[@id='" + phrase_name + "']/xmlns:word",
            self.namespace)[word_position]

        return words

    def _find_globaltags(self, globaltag_name):
        (phrase_name, globaltag_position) = self._find_child_position(globaltag_name, "globaltags")

        globaltags = self.tree.findall("xmlns:phrase[@id='" + phrase_name + "']/xmlns:globaltags",
            self.namespace)[globaltag_position]

        return globaltags

    def _next_id(self, name):
        current_id = self._tier_information[name]['id']

        self._tier_information[name]['id'] = current_id + 1
        self._tier_information[name]['last_id'] = current_id

        return current_id

    def _find_child_position(self, name, linguistic_type):
        for child in self._tier_information[linguistic_type]['childs']:
            if child['id'] == name:
                return child['parent_id'], child['position']

    def region_for_annotation(self, annotation):
        pass

    def tier_has_regions(self, tier):
        pass