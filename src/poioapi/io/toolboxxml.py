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
        self._elements_map = {"itmGroup": [], "idGroup": {}, "txGroup": {},
                              "tx": {}, "mr": {}, "mg": {}}

        self.parse_element_tree(tree)

    def parse_element_tree(self, tree):
        for t in tree:
            if t.tag == "itmGroup":
                self._current_itmGroup = t.find("itm").text
                self._elements_map["itmGroup"].append(
                    {"id": self._current_itmGroup, "value": t.find("ti").text,
                     "features": {'sp': t.find("sp").text}})

            elif t.tag == "idGroup":
                self._current_idGroup = t.find("id").text
                value, region = self._split_region(t)
                fg = None

                if len(t.find("fg")) > 0:
                    fg = t.find("fg").text

                self._add_elment_to_elements(t, self._current_idGroup,
                                             self._current_itmGroup, value, {"fg": fg}, region)

            elif t.tag == "txGroup":
                self._current_txGroup = self._next_id()
                self._add_elment_to_elements(t, self._current_txGroup, self._current_idGroup)

            elif t.tag == "tx":
                self._current_tx = self._next_id()
                self._add_elment_to_elements(t, self._current_tx, self._current_txGroup, t.text)

            elif t.tag == "mg" or t.tag == "mr":
                self._add_elment_to_elements(t, self._next_id(), self._current_tx, t.text)

            if len(t.getchildren()) > 0:
                self.parse_element_tree(t)

    def _add_elment_to_elements(self, t, id, parent=None, value=None, features=None, region=None):
        if (t.tag, parent) in self._elements_map:
            self._elements_map[(t.tag, parent)].append(
                {"id": id, "value": value, "region": region, "features": features})
        else:
            self._elements_map[(t.tag, parent)] = [{"id": id, "value": value,
                                                    "region": region,
                                                    "features": features}]

    def get_root_tiers(self):
        return [poioapi.io.graf.Tier("itmGroup")]

    def get_child_tiers_for_tier(self, tier):
        if tier.name == "itmGroup":
            return [poioapi.io.graf.Tier("idGroup")]
        if tier.name == "idGroup":
            return [poioapi.io.graf.Tier("txGroup")]
        if tier.name == "txGroup":
            return [poioapi.io.graf.Tier("tx")]
        if tier.name == "tx":
            return [poioapi.io.graf.Tier("mr"),
                    poioapi.io.graf.Tier("mg")]

    def get_annotations_for_tier(self, tier, annotation_parent=None):
        if tier.name == "itmGroup":
            return [poioapi.io.graf.Annotation(e["id"], e["value"],
                                               e["features"])
                    for e in self._elements_map[tier.name]]

        else:
            if (tier.name, annotation_parent.id) in self._elements_map:
                return [poioapi.io.graf.Annotation(e["id"], e["value"],
                                                   e["features"])
                        for e in self._elements_map[(tier.name, annotation_parent.id)]]
            else:
                return []

    def tier_has_regions(self, tier):
        if tier.name == "idGroup":
            return True

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
