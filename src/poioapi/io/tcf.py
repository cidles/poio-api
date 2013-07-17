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

from __future__ import unicode_literals

import xml.etree.ElementTree as ET

import poioapi.io.graf


class Parser(poioapi.io.graf.BaseParser):
    """
    Class that will handle parse of TCF files.

    """

    def __init__(self, filepath):
        """Class's constructor.

        Parameters
        ----------
        filepath : str
            Path of the elan file.

        """

        self.filepath = filepath
        self.parse()

    def parse(self):
        """This method will set the variables
        to make possible to do the parsing
        correctly.

        """

        self.root = ET.parse(self.filepath).getroot()
        self.namespace = "{http://www.dspin.de/data/textcorpus}"
        self.tree = self.root.find("{0}TextCorpus".format(self.namespace))
        self._current_id = 0

    def get_root_tiers(self):
        """This method retrieves all the root tiers.

        Returns
        -------
        list : array-like
            List of tiers type.

        """

        return [poioapi.io.graf.Tier("sentences")]

    def get_child_tiers_for_tier(self, tier):
        """This method retrieves all the child tiers
        of a specific tier.

        Parameters
        ----------
        tier : object
            Tier to find the children from.

        Returns
        -------
        child_tiers : array-like
            List of tiers type.

        """

        if tier.name == "sentences":
            return [poioapi.io.graf.Tier("tokens")]
        elif tier.name == "tokens":
            return [poioapi.io.graf.Tier("POStags"),
                    poioapi.io.graf.Tier("lemmas")]

    def get_annotations_for_tier(self, tier, annotation_parent=None):
        """This method retrieves all the annotations
        of a specific tier.

        Parameters
        ----------
        tier : object
            Tier to find the annotations.
        annotation_parent : object
            Annotation parent it is the reference.

        Returns
        -------
        annotations : array-like
            List of annotations type.

        """

        annotations = []

        if tier.name == "sentences":
            sentences = self.tree.find("{0}sentences".format(self.namespace))
            for s in sentences.findall("{0}sentence".format(self.namespace)):
                annotations.append(poioapi.io.graf.Annotation(s.attrib["ID"], s.attrib["tokenIDs"]))

        elif tier.name == "tokens":
            for tokens in self.tree.findall("{0}tokens".format(self.namespace)):
                for t in tokens:
                    if t.attrib["ID"] in annotation_parent.value:
                        annotations.append(poioapi.io.graf.Annotation(t.attrib["ID"], t.text))

        elif tier.name == "POStags":
            for tags in self.tree.findall("{0}POStags".format(self.namespace)):
                for t in tags:
                    if t.attrib["tokenIDs"] == annotation_parent.id:
                        annotations.append(poioapi.io.graf.Annotation(self._next_id(), t.text))

        elif tier.name == "lemmas":
            for lemmas in self.tree.findall("{0}lemmas".format(self.namespace)):
                for l in lemmas:
                    if l.attrib["tokenIDs"] == annotation_parent.id:
                        annotations.append(poioapi.io.graf.Annotation(l.attrib["ID"], l.text))

        return annotations

    def _next_id(self):
        current_id = str(int(self._current_id) + 1)
        self._current_id = current_id

        return current_id

    def tier_has_regions(self, tier):
        if tier.name == "sentences":
            return True

        return False

    def region_for_annotation(self, annotation):
        sentences = self.tree.find("{0}sentences".format(self.namespace))
        for s in sentences.findall("{0}sentence".format(self.namespace)):
            if s.attrib["ID"] == annotation.id:
                return s.attrib["start"], s.attrib["end"]

    def get_primary_data(self):
        """This method gets the information about
        the source data file.

        Returns
        -------
        primary_data : object
            PrimaryData object.

        """

        primary_data = poioapi.io.graf.PrimaryData()
        primary_data.type = primary_data.TEXT
        primary_data.content = self.tree.find("{0}text".format(self.namespace)).text

        return primary_data