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
import re

import xml.etree.ElementTree as ET

from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

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

        return [poioapi.io.graf.Tier("text")]

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

        if tier.name == "text":
            return [poioapi.io.graf.Tier("token")]
        elif tier.name == "token":
            return [poioapi.io.graf.Tier("tag"),
                    poioapi.io.graf.Tier("lemma")]

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

        if tier.name == "text":
            return [poioapi.io.graf.Annotation("t{0}".format(self._next_id()), t.text)
                    for t in self.tree.findall("{0}text".format(self.namespace))]
        elif tier.name == "token":
            for tokens in self.tree.findall("{0}tokens".format(self.namespace)):
                for t in tokens:
                    annotations.append(poioapi.io.graf.Annotation(t.attrib["ID"], t.text))
        elif tier.name == "tag":
            for tags in self.tree.findall("{0}POStags".format(self.namespace)):
                for t in tags:
                    if t.attrib["tokenIDs"] == annotation_parent.id:
                        annotations.append(poioapi.io.graf.Annotation(self._next_id(), t.text))
        elif tier.name == "lemma":
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
        pass

    def region_for_annotation(self, annotation):
        pass