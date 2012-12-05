# -*- coding: utf-8 -*-
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
"""
This module contains classes to access Elan data.

The class Eaf is a low level API to .eaf files.

EafGlossTree, EafPosTree, etc. are the classes to access the data via
tree, which also contains the original .eaf IDs. Because of this
EafTrees are read-/writeable.

"""

# Elan file
import codecs
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

class ElanHandler(ContentHandler):
    """
    Class that handles the XML test_split.

    The class uses the ContentHandler from
    SAX XML.
    """

    def __init__(self):
        self.tokenizer = []

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

        """
        # First element of the all document
        if name == 'ANNOTATION_DOCUMENT':
            for attr_name in attrs.getNames():
                print(str(attr_name) + " - " + str(attrs.getValue(attr_name)))

        # HEADER
        if name == 'HEADER':
            for attr_name in attrs.getNames():
                print(str(attr_name) + " - " + str(attrs.getValue(attr_name)))

        # HEADER subelement
        if name == 'MEDIA_DESCRIPTOR':
            for attr_name in attrs.getNames():
                print(str(attr_name) + " - " + str(attrs.getValue(attr_name)))

        # HEADER subelement
        if name == 'LINKED_FILE_DESCRIPTOR':
            for attr_name in attrs.getNames():
                print(str(attr_name) + " - " + str(attrs.getValue(attr_name)))

        # HEADER subelement
        if name == 'PROPERTY':
            for attr_name in attrs.getNames():
                print(str(attr_name) + " - " + str(attrs.getValue(attr_name)))

        # HEADER subelement - Optional
        if name == 'MEDIA_FILE':
            for attr_name in attrs.getNames():
                print(str(attr_name) + " - " + str(attrs.getValue(attr_name)))

        # HEADER subelement - Optional
        if name == 'TIME_UNITS':
            for attr_name in attrs.getNames():
                print(str(attr_name) + " - " + str(attrs.getValue(attr_name)))

        # TIME_ORDER is createad with the TIME_SLOT elements
        if name == 'TIME_SLOT':
            for attr_name in attrs.getNames():
                print(str(attr_name) + " - " + str(attrs.getValue(attr_name)))

        # TIERS is a container for a sequence of ANNOTATIONs
        if name == 'TIER':
            for attr_name in attrs.getNames():
                print(str(attr_name) + " - " + str(attrs.getValue(attr_name)))
        """
        # The ANNOTATION don't need to be read only theirs elements

        # ANNOTATION subelement
        if name == 'ALIGNABLE_ANNOTATION':
            for attr_name in attrs.getNames():
                print(str(attr_name) + " - " + str(attrs.getValue(attr_name)))

        # DONT FORGET THE ANNOTATION VALUE

        # ANNOTATION subelement
        if name == 'REF_ANNOTATION':
            for attr_name in attrs.getNames():
                print(str(attr_name) + " - " + str(attrs.getValue(attr_name)))

    def characters (self, ch):
        pass

    def endElement(self, name):
        pass

class ElanContentHandler:
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
        self.metafile = metafile

    def parse(self):
        """Return the tokens of the regions parsed
        by the class XmlHandler.

        """

        parser = make_parser()
        curHandler = ElanHandler()
        parser.setContentHandler(curHandler)
        f = codecs.open(self.metafile, 'r', 'utf-8')
        parser.parse(f)
        f.close()

file = 'C:/tests/elan/example.eaf'

content = ElanContentHandler(file)
content.parse()