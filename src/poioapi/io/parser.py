# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
""" This modules contains a class that uses
the ContentHandler from SAX Xml.
"""

import codecs

from xml.sax import make_parser
from xml.sax.handler import ContentHandler

class XmlHandler(ContentHandler):

    def __init__(self):
        self.regions_list = []
        self.features_list = []
        self.link = ''
        self.edge_from = ''
        self.map = {}
        self.tag = ''
        self._root_element = 0
        self._buffer = ""
        self.hasregion = False
        self.elan_list = []
        self.tier_id = ''
        self.cv_id = ''
        self.time_slot_dict = dict()
        self.constraints_list = []
        self.linguistic_type_list = []

    def startElement(self, name, attrs):

        self.map[name] = ''
        self.tag = name

        if name == 'link':
            self.link = attrs.getValue('targets')

        if name == 'region':
            id = attrs.getValue('xml:id')
            att = attrs.getValue('anchors')
            tokenizer = att.split()
            values = (id, tokenizer,
                      self.edge_from)
            self.regions_list.append(values)
            self.hasregion = True

        if name == 'edge':
            self.edge_from = attrs.getValue('from')

        if name == 'a':
            ref = attrs.getValue('ref')
            id = attrs.getValue('xml:id')

            if self.hasregion:
                self.values = (id, self.edge_from)
            else:
                self.values = (id, ref)

        # Elan parser - Xml tags
        values_list = []

        if name == 'TIER' or name == 'CONTROLLED_VOCABULARY':
            for attr_name in attrs.getNames():
                if attr_name == 'TIER_ID':
                    self.tier_id = attrs.getValue(attr_name)
                elif attr_name == 'CV_ID':
                    self.cv_id = attrs.getValue(attr_name)
                value = attr_name + " - " + attrs.getValue(attr_name)
                values_list.append(value)
            self.elan_list.append((name, values_list))
        elif name == 'ALIGNABLE_ANNOTATION' or name == 'REF_ANNOTATION' or name == 'CV_ENTRY':
            if name == 'CV_ENTRY':
                depends = "DEPENDS - " + self.cv_id
            else:
                depends = "DEPENDS - " + self.tier_id

            for attr_name in attrs.getNames():
                value = attr_name + " - " + attrs.getValue(attr_name)
                values_list.append(value)
            self.elan_list.append((name, values_list, depends))
        elif name == 'TIME_SLOT':
            key = ''
            key_entry = ''
            for attr_name in attrs.getNames():
                if attr_name == 'TIME_SLOT_ID':
                    key = attrs.getValue(attr_name)
                else:
                    if attrs.getValue(attr_name) is not None:
                        key_entry = attrs.getValue(attr_name)
                    else:
                        key_entry = '0'

            self.time_slot_dict[key] = key_entry
        elif name == 'CONSTRAINT':
            for attr_name in attrs.getNames():
                value = attr_name + " - " + attrs.getValue(attr_name)
                values_list.append(value)
            self.constraints_list.append(values_list)
        elif name == 'LINGUISTIC_TYPE':
            for attr_name in attrs.getNames():
                value = attr_name + " - " + attrs.getValue(attr_name)
                values_list.append(value)
            self.linguistic_type_list.append(values_list)
        else:
            for attr_name in attrs.getNames():
                value = attr_name + " - " + attrs.getValue(attr_name)
                values_list.append(value)

            if len(values_list) is not 0:
                self.elan_list.append((name, values_list))

    def characters (self, ch):
        self.map[self.tag] += ch

        # Check for root node
        if self._root_element == 1:
            self._buffer += ch

    def endElement(self, name):
        if name=='f':
            values = self.values
            id = values[0]
            ref = values[1]
            self.features_list.append((id, self.map[name], ref))

        if name=='ANNOTATION_VALUE' or name=='CV_ENTRY':
            tuple_value = self.elan_list[-1]
            tuple_value = tuple_value + ("VALUE - " + self.map[name], )
            self.elan_list[-1] = tuple_value

class XmlContentHandler:
    """
    Class that handles the Xml files like.

    The class uses the ContentHandler from
    SAX XML.
    """

    def __init__(self, metafile):
        """Class's constructor.

        Parameters
        ----------
        metafile : str
            Path of the file to manipulate.

        """

        self.metafile = metafile

    def parse(self):
        """Return the important information about the
        different files (e.g. GrAF, elan,...). The gathered
        information contains tokens, regions and all the need
        data that will be used to help in the creation of the
        GrAF objects from the files or to create GrAF files
        from the same kind of files.

        """

        parser = make_parser()
        xml_handler = XmlHandler()
        parser.setContentHandler(xml_handler)

        # Handle the files encode
        try:
            f = codecs.open(self.metafile, 'r', 'utf-8')
            parser.parse(f)
        except UnicodeEncodeError as unicodeError:
            print(unicodeError)

            f = open(self.metafile, 'r')
            parser.parse(f)

        f.close()

        self.features_list = xml_handler.features_list
        self.regions_list = xml_handler.regions_list
        self.elan_list = xml_handler.elan_list
        self.time_slot_dict = xml_handler.time_slot_dict
        self.constraints_list = xml_handler.constraints_list
        self.linguistic_type_list = xml_handler.linguistic_type_list