# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
""" This module is to parse the files.

"""

import codecs

from xml.sax import make_parser
from xml.sax.handler import ContentHandler

class XmlHandler(ContentHandler):
    """
    Class that handles the XML test_split.

    The class uses the ContentHandler from
    SAX XML.
    """

    def __init__(self):
        self.tokenizer = []
        self.token_id = []
        self.tokens_map = []
        self.features_map = []
        self.link = ''
        self.edge_from = ''
        self.map = {}
        self.tag = ''
        self._root_element = 0
        self._buffer = ""
        self.hasregion = False
        self.elan_map = []
        self.tier_id = ''
        self.cv_id = ''
        self.time_slot_dict = dict()

    def startElement(self, name, attrs):
        """Method from ContentHandler Class.

        Need each line of the xml file.

        Parameters
        ----------
        `name` : str
            Name of the tag.
        attrs : SAX type
            Instance of a line of the xml.

        """

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
            self.tokens_map.append(values)
            self.hasregion = True

            # Need to write the regions
            id = id.split('-r')
            self.tokenizer.append(tokenizer)
            self.token_id.append(id[1])

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
            self.elan_map.append((name, values_list))
        elif name == 'ALIGNABLE_ANNOTATION' or name == 'REF_ANNOTATION' or name == 'CV_ENTRY':
            if name == 'CV_ENTRY':
                depends = "DEPENDES - " + self.cv_id
            else:
                depends = "DEPENDES - " + self.tier_id

            for attr_name in attrs.getNames():
                value = attr_name + " - " + attrs.getValue(attr_name)
                values_list.append(value)
            self.elan_map.append((name, values_list, depends))
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
        else:
            for attr_name in attrs.getNames():
                value = attr_name + " - " + attrs.getValue(attr_name)
                values_list.append(value)

            if len(values_list) is not 0:
                self.elan_map.append((name, values_list))

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
            self.features_map.append((id, self.map[name], ref))

        if name=='ANNOTATION_VALUE' or name=='CV_ENTRY':
            tuple_value = self.elan_map[-1]
            tuple_value = tuple_value + ("VALUE - " + self.map[name], )
            self.elan_map[-1] = tuple_value

class XmlContentHandler:
    """
    Class that handles the XML test_split.

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

        self.tokenizer = []
        self.token_id = []
        self.features_map = []
        self.tokens_map = []
        self.metafile = metafile

    def parse(self):
        """Return the tokens of the regions parsed
        by the class XmlHandler.

        """

        parser = make_parser()
        xml_handler = XmlHandler()
        parser.setContentHandler(xml_handler)
        f = codecs.open(self.metafile, 'r', 'utf-8')
        parser.parse(f)
        f.close()

        self.tokenizer = xml_handler.tokenizer
        self.token_id = xml_handler.token_id
        self.features_map = xml_handler.features_map
        self.tokens_map = xml_handler.tokens_map
        self.elan_map = xml_handler.elan_map
        self.time_slot_dict = xml_handler.time_slot_dict