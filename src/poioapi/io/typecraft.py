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
        self._current_phrase_id = 0
        self._current_id = None

    def get_root_tiers(self):
        return [poioapi.io.graf.Tier("phrase")]

    def get_child_tiers_for_tier(self, tier):
        if tier.name == "phrase":
            return [poioapi.io.graf.Tier("word"),
                    poioapi.io.graf.Tier("translation"),
                    poioapi.io.graf.Tier("description")]

        elif tier.name == "word":
            return [poioapi.io.graf.Tier("pos"),
                    poioapi.io.graf.Tier("morpheme")]

        elif tier.name == "morpheme":
            return [poioapi.io.graf.Tier("gloss")]

    def get_annotations_for_tier(self, tier, annotation_parent=None):
        if tier.name == "phrase":
            return [self._element_as_annotation(annotation, "original")
                    for annotation in self.tree.findall("xmlns:phrase",
                self.namespace)]

        elif tier.name == "word" or tier.name == "translation" or \
             tier.name == "description":
            return self._get_child_phrases(tier, annotation_parent)

        elif tier.name == "pos" or tier.name == "morpheme":
            return self._get_child_words(tier, annotation_parent)

        elif tier.name == "gloss":
            return self._get_child_morphemes(tier, annotation_parent)

    def _get_child_phrases(self, tier, annotation_parent):
        for phrase in self.tree.findall("xmlns:phrase", self.namespace):
            if phrase.attrib["id"] == annotation_parent.id:
                return [self._element_as_annotation(annotation, tier.name)
                        for annotation in phrase.findall("xmlns:"+tier.name,
                    self.namespace)]

    def _get_child_words(self, tier, annotation_parent):
        for phrase in self.tree.findall("xmlns:phrase", self.namespace):
            if phrase.attrib["id"] == annotation_parent.features["parent_phrase"]:
                for word in phrase.findall("xmlns:word", self.namespace):
                    features = self._get_features(word.attrib)
                    diff = set(annotation_parent.features.keys()) -\
                           set(features.keys())
                    if len(diff) == 1 or len(diff) == 0 and diff == "parent_phrase":
                        return [self._element_as_annotation(element, tier.name)
                                for element in word
                                if element.tag == "{" + self.namespace['xmlns']
                                                  + "}" + tier.name]

    def _get_child_morphemes(self, tier, annotation_parent):
        for phrase in self.tree.findall("xmlns:phrase", self.namespace):
            if phrase.attrib["id"] == annotation_parent.features["parent_phrase"]:
                for word in phrase.findall("xmlns:word", self.namespace):
                    for m in word.findall("xmlns:morpheme", self.namespace):
                        features = self._get_features(m.attrib)
                        diff = set(annotation_parent.features.keys()) -\
                               set(features.keys())
                        if len(diff) == 1 or len(diff) == 0 and diff == "parent_phrase":
                            return [self._element_as_annotation(element, tier.name)
                                    for element in m
                                    if element.tag == "{" + self.namespace['xmlns']
                                                      + "}" + tier.name]

    def _element_as_annotation(self, element, value_key = None):
        features = self._get_features(element.attrib)
        features["parent_phrase"] = self._current_phrase_id
        value = None

        if "id" in features:
            id = features["id"]
            self._current_phrase_id = id
            self._current_id = id
        else:
            id = self._next_id()

        if "text" in features:
            value = features["text"]
            features.pop("text")
        elif value_key == "pos" or value_key == "gloss" or \
             value_key == "description" or value_key == "translation":
            value = element.text
        else:
            for el in element:
                if el.tag == "{" + self.namespace['xmlns'] + "}" + value_key:
                    value = el.text

        return poioapi.io.graf.Annotation(id, value, features)

    def _get_features(self, attributes):
        features = {}

        for key, value in attributes.items():
            features[key] = value

        return features

    def _next_id(self):
        current_id = str(int(self._current_id) + 1)
        self._current_id = current_id

        return current_id

    def region_for_annotation(self, annotation):
        pass

    def tier_has_regions(self, tier):
        pass