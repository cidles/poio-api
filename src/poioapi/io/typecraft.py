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

import xml.etree.cElementTree as ET
from xml.etree.ElementTree import tostring
from xml.dom import minidom

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
        self._current_id = 0
        self._elements_map = {"phrase": [], "word": [], "translation": [],
                              "description": [], "pos": [], "morpheme": [],
                              "gloss": []}

        self.parse_element_tree(self.tree)

    def parse_element_tree(self, tree):
        for element in tree:
            if element.tag == "{" + self.namespace['xmlns'] + "}" + "phrase":
                self._elements_map["phrase"].append({"id": element.attrib["id"],
                                                     "attrib": element.attrib})
                self._current_phrase_id = element.attrib["id"]
            elif element.tag == "{" + self.namespace['xmlns'] + "}" + "original":
                for i, el in enumerate(self._elements_map["phrase"]):
                    if el["id"] == self._current_phrase_id:
                        el["value"] = element.text
                        self._elements_map["phrase"][0] = el

            elif element.tag == "{" + self.namespace['xmlns'] + "}" + "word":
                self._current_word_id = self._next_id()
                self._elements_map["word"].append({"id": self._current_word_id,
                                                   "attrib": element.attrib,
                                                   "parent": self._current_phrase_id})
            elif element.tag == "{" + self.namespace['xmlns'] + "}" + "pos":
                self._elements_map["pos"].append({"id": self._next_id(),
                                                  "value": element.text,
                                                  "parent": self._current_word_id})
            elif element.tag == "{" + self.namespace['xmlns'] + "}" + "morpheme":
                self._current_morpheme_id = self._next_id()
                self._elements_map["morpheme"].append({"id": self._current_morpheme_id,
                                                       "attrib": element.attrib,
                                                       "parent": self._current_word_id})
            elif element.tag == "{" + self.namespace['xmlns'] + "}" + "gloss":
                self._elements_map["gloss"].append({"id": self._next_id(),
                                                    "value": element.text,
                                                    "parent": self._current_morpheme_id})
            elif element.tag == "{" + self.namespace['xmlns'] + "}" + "description":
                self._elements_map["description"].append({"id": self._next_id(),
                                                          "value": element.text,
                                                          "parent": self._current_phrase_id})
            elif element.tag == "{" + self.namespace['xmlns'] + "}" + "translation":
                self._elements_map["translation"].append({"id": self._next_id(),
                                                          "value": element.text,
                                                          "parent": self._current_phrase_id})
            if len(element.getchildren()) > 0:
                self.parse_element_tree(element)

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
            return [poioapi.io.graf.Annotation(e["id"], e["value"],
                                               self._get_features(e["attrib"]))
                    for e in self._elements_map[tier.name]]

        elif tier.name == "word" or tier.name == "morpheme":
            annotations = []
            for e in self._elements_map[tier.name]:
                if e["parent"] == annotation_parent.id:
                    features = self._get_features(e["attrib"])
                    value = e["attrib"]["text"]
                    annotations.append(poioapi.io.graf.Annotation(e["id"],
                                                                  value, features))

            return annotations

        else:
            return [poioapi.io.graf.Annotation(e["id"], e["value"])
                    for e in self._elements_map[tier.name]
                    if e["parent"] == annotation_parent.id]

    def get_primary_data(self):
        """This method gets the information about
        the source data file.

        Returns
        -------
        primary_data : object
            PrimaryData object.

        """

        primary_data = poioapi.io.graf.PrimaryData()
        primary_data.type = poioapi.io.graf.NONE
        primary_data.filename = "unknown"

        return primary_data

    def _get_features(self, attributes):
        features = {}

        for key, value in attributes.items():
            if key != "id":
                if key != "text":
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


class Writer(poioapi.io.graf.BaseWriter):
    """

    """

    def write(self, outputfile, converter):

        nodes = converter.graf.nodes
        phrases = self._get_phrases(nodes)

        self._current_id = 0

        attribs = {"xsi:schemaLocation": "http://typecraft.org/typecraft.xsd",
                   "xmlns": "http://typecraft.org/typecraft",
                   "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance"}

        root = ET.Element("typecraft", attribs)

        # The language must be set as und
        text = ET.SubElement(root, "text", {"id": self._next_id(), "lang": "und"})
        ET.SubElement(text, "title").text = converter.meta_information
        ET.SubElement(text, "titleTranslation")
        ET.SubElement(text, "body").text = self._get_body(phrases)

        for p in phrases:
            phrase = ET.SubElement(text, "phrase", {"id": self._next_id(), "valid": "VALID"})
            ET.SubElement(phrase, "original").text = p.annotations._elements[0].features["annotation_value"]
            ET.SubElement(phrase, "translation")
            ET.SubElement(phrase, "description")
            ET.SubElement(phrase, "globaltags", {"id": "1", "tagset": "Default"})

            for w in self._get_words(nodes, p.id):
                value = w.annotations._elements[0].features["annotation_value"]
                word = ET.SubElement(phrase, "word", {"text": value, "head": value})
                for m in self._get_morphemes(nodes, w.id):
                    value = m.annotations._elements[0].features["annotation_value"]
                    ET.SubElement(word, "pos").text = self._get_pos_value(nodes, m.id)
                    morpheme = ET.SubElement(word, "morpheme", {"text": value, "baseform": value})
                    for g in self._get_glosses(nodes, m.id):
                        if g.annotations._elements[0].features:
                            value = g.annotations._elements[0].features["annotation_value"]
                            ET.SubElement(morpheme, "gloss").text = value

        self.write_xml(root, outputfile, False)

    def write_xml(self, root, outputfile, pretty_print=True):
        if pretty_print:
            doc = minidom.parseString(tostring(root))

            file = open(outputfile, 'wb')
            file.write(doc.toprettyxml(encoding='UTF-8'))
            file.close()
        else:
            tree = ET.ElementTree(root)
            tree.write(outputfile)

    def _get_phrases(self, nodes):
        return [node for node in nodes if node.id.startswith("ref")]

    def _get_body(self, phrases, body=""):
        for n in phrases:
            body += n.annotations._elements[0].features["annotation_value"]

        return body

    def _get_words(self, nodes, parent_id):
        return [node for node in nodes
                if node.id.startswith("t") and
                   node.parent.id == parent_id]

    def _get_pos_value(self, nodes, parent_id):
        for node in nodes:
            if node.id.startswith("p") and node.parent.id == parent_id:
                if node.annotations._elements[0].features:
                    return node.annotations._elements[0].features["annotation_value"]
                return ""

    def _get_morphemes(self, nodes, parent_id):
        return [node for node in nodes
                if node.id.startswith("m") and
                   node.parent.id == parent_id]

    def _get_glosses(self, nodes, parent_id):
        return [node for node in nodes
                if node.id.startswith("g") and
                   node.parent.id == parent_id]

    def _next_id(self):
        current_id = str(int(self._current_id) + 1)
        self._current_id = current_id

        return str(current_id)