# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

"""

"""

from __future__ import absolute_import

import re

import xml.etree.ElementTree as ET

import poioapi.io.graf


class Parser(poioapi.io.graf.BaseParser):

    def __init__(self, filepath):
        """Class's constructor.

        Parameters
        ----------
        filepath : str
            Path of the Toolbox XML file.

        """

        self.filepath = filepath
        self.parse()

    def parse(self):
        """This method will parse the input file.

        """

        root = ET.parse(self.filepath)
        tree = root.getroot()
        self._current_id = 0
        self._elements_map = {"ref": [], "t": {}, "m": {},
                              "g": {}, "p": {}, "f": {}}

        self.parse_element_tree(tree)

    def parse_element_tree(self, tree):
        """
        tag name and value represent the title
        ref represents the
        """
        for t in tree:
            if t.tag == "ref":
                self._current_ref = t.attrib['value']
                self._elements_map["ref"].append({"id":self._current_ref, "value":""})

            elif t.tag == "t":
                self._current_t = self._next_id()
                self._add_elment_to_elements(t, self._current_t, self._current_ref,
                                             t.attrib['value'])
                self._add_phrase(t.attrib['value'])

            elif t.tag == "p":
                if t.text and "-" not in t.text:
                    self._add_elment_to_elements(t, self._next_id(), self._current_t,
                                                 t.text)

            elif t.tag == "m":
                self._current_m = self._next_id()
                self._add_elment_to_elements(t, self._current_m, self._current_t,
                                             t.attrib['value'])

            elif t.tag == "g":
                self._add_elment_to_elements(t, self._next_id(), self._current_m, t.text)

            elif t.tag == "name":
                self.meta_information = t.attrib["value"]

            if len(t.getchildren()) > 0:
                self.parse_element_tree(t)

    def _add_phrase(self, value):
        for ref in self._elements_map["ref"]:
            if ref["id"] == self._current_ref:
                ref["value"] += value + " "


    def _add_elment_to_elements(self, t, id, parent=None, value=None, features=None, region=None):
        if (t.tag, parent) in self._elements_map:
            self._elements_map[(t.tag, parent)].append(
                {"id": id, "value": value, "region": region, "features": features})
        else:
            self._elements_map[(t.tag, parent)] = [{"id": id, "value": value,
                                                    "region": region,
                                                    "features": features}]

    def get_root_tiers(self):
        return [poioapi.io.graf.Tier("ref")]

    def get_child_tiers_for_tier(self, tier):
        if tier.name == "ref":
            return [poioapi.io.graf.Tier("t")]
        if tier.name == "t":
            return [poioapi.io.graf.Tier("p"),
                    poioapi.io.graf.Tier("m")]
        if tier.name == "m":
            return [poioapi.io.graf.Tier("g")]

    def get_annotations_for_tier(self, tier, annotation_parent=None):
        if tier.name == "ref":
            return [poioapi.io.graf.Annotation(e["id"], e['value'])
                    for e in self._elements_map[tier.name]]

        else:
            if (tier.name, annotation_parent.id) in self._elements_map:
                return [poioapi.io.graf.Annotation(e["id"], e["value"],
                                                   e["features"])
                        for e in self._elements_map[(tier.name, annotation_parent.id)]]
            else:
                return []

    def tier_has_regions(self, tier):
        #if tier.name == "t":
        #    return True

        return False

    def region_for_annotation(self, annotation):
        idGroup = [value for key, value in self._elements_map.items()
                   if "idGroup" in key]

        for elements in idGroup:
            for e in elements:
                if e["id"] == annotation.id:
                    return e["region"]

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
        primary_data.type = poioapi.io.graf.NONE
        primary_data.filename = "unknown"

        return primary_data

    def _next_id(self):
        current_id = str(int(self._current_id) + 1)
        self._current_id = current_id

        return current_id

    def _split_region(self, element):
        try:
            aud = element.find("aud").text
            results = re.findall("\d*\.\d+|\d+", aud)

            region = (results[-2], results[-1])
            value = aud.split(results[-2])[0]
        except:
            value = None
            region = None

        return value, region