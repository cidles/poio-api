# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

import os
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

from poioapi import data
from poioapi.io import elan

class TestElan:
    """
    This class contain the test methods to the
    class io.elan.py.

    """

    def setup(self):
        self.filename = os.path.join(os.path.dirname(__file__), "sample_files",
            "elan_graf", "example.eaf")

        self.basedirname = os.path.dirname(self.filename)

        self.metafile = os.path.join(os.path.dirname(__file__), "sample_files",
            "elan_graf", "example-extinfo.xml")

        data_structure = ['utterance',['clause',['word']],'translation']

        # Initialize the Elan class
        self.elan = elan.Elan(self.filename, data.DataStructureTypeWithConstraints(data_structure))

    def test_find_hierarchy_parents(self):
        expected_result = {'clause': 'utterance',
                           'translation': 'utterance',
                           'utterance': None,
                           'word': 'clause'}

        self.elan._find_hierarchy_parents(self.elan.data_structure_hierarchy, None)

        final_result = self.elan.data_hierarchy_parent_dict

        assert(final_result == expected_result)

    def test_write_elan(self):
        root = self.elan.write_elan(self.metafile)

        miscellaneous = root.find('./file/miscellaneous')

        top_element = miscellaneous[0]
        new_element_tree = Element(top_element.tag, top_element.attrib)

        for element in miscellaneous.iter():
            if element.tag == 'TIER':
                self.elan._find_tier_elements(None,None)

            print(element.tag)

            SubElement(new_element_tree, element.tag, element.attrib).text = element.text

        file = open(self.basedirname+"/_result.xml",'wb')
        doc = minidom.parseString(tostring(new_element_tree))
        file.write(doc.toprettyxml(indent='  ', encoding='utf-8'))
        file.close()

        assert(1 != 1)