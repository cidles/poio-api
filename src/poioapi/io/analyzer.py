# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
""" This document contain the methods to 
parse all the files that were generated with 
the GrAF ISO format.
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

    def get_tokenizer(self):
        return self.tokenizer

    def get_token_id(self):
        return self.token_id

    def get_features_map(self):
        return self.features_map

    def get_tokens_map(self):
        return self.tokens_map

class ProcessContent:
    """
    Class that handles the XML files.

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

    def process(self):
        """Return the tokens of the regions parsed
        by the class XmlHandler.

        """

        parser = make_parser()
        curHandler = XmlHandler()
        parser.setContentHandler(curHandler)
        f = codecs.open(self.metafile, "r", "utf-8")
        parser.parse(f)
        f.close()
        self.tokenizer = curHandler.get_tokenizer()
        self.token_id = curHandler.get_token_id()
        self.features_map = curHandler.get_features_map()
        self.tokens_map = curHandler.get_tokens_map()

    def get_tokenizer(self):
        return self.tokenizer

    def get_token_id(self):
        return self.token_id

    def get_features_map(self):
        return self.features_map

    def get_tokens_map(self):
        return self.tokens_map
