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
        primary_data.type = poioapi.io.graf.TEXT
        primary_data.content = self.tree.find("{0}text".format(self.namespace)).text

        return primary_data

class Writer(poioapi.io.graf.BaseWriter):
    """
    Class that will handle the writing of
    GrAF files into Elan files again.

    """

    def write(self, outputfile, converter):
        """Write the GrAF object into a Elan file.

        Parameters
        ----------
        outputfile : str
            The filename of the output file. The filename should have
            the Elan extension ".eaf".
        graf_graph : obejct
            A GrAF object.
        tier_hierarchies : array_like
            Array with all the tier hierarchies from the GrAF.
        primary_data : object
            This object will contain the information to the dataDesc
            primaryData.
        meta_information : ElementTree
            Element tree contains all the information in Elan file
            besides the Tiers annotations.

        """

        self.root = ET.Element('D-Spin', { 'xmlns': 'http://www.dspin.de/data', 'version': '0.4', 'xmlns:ed': 'http://www.dspin.de/data/extdata' })
        meta = ET.SubElement(self.root, 'MetaData', { 'xmlns': 'http://www.dspin.de/data/metadata' })
        source = ET.SubElement(meta, 'source')
        source.text = "Poio API conversion"
        
        external = ET.SubElement(self.root, "ed:ExternalData")
        ext_type = None
        if converter.primary_data.type == "audio":
            ext_type = "audio/wav"
        elif converter.primary_data.type == "video":
            ext_type = "video/mpeg"
        if ext_type:
            signal = ET.SubElement(external, 'ed:speechsignal', { 'type': ext_type, })
            if converter.primary_data.external_link:
                signal.text = converter.primary_data.external_link
            elif converter.primary_data.filename:
                signal.text = converter.primary_data.filename
        if converter.original_file:
            seg = ET.SubElement(external, 'ed:phoneticsegmentation', { 'type': 'text/eaf+xml' })
            seg.text = converter.original_file

        self._write_file(outputfile)

    def _write_file(self, outputfile):
        stream = outputfile
        was_stream = True
        if not hasattr(stream, 'read'):
            stream = open(outputfile, 'wb')
            was_stream = False
        doc = minidom.parseString(ET.tostring(self.root))
        str_content = doc.toprettyxml(indent='    ', encoding='UTF-8')
        stream.write(str_content)
        if not was_stream:
            stream.close()