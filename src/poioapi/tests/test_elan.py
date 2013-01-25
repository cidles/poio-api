# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

import os
import re
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.etree.ElementTree as ET

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
        self.elan = elan.Elan(self.filename, data_structure)

    def test_write_elan(self):
        # compare the result file with
        # the original
        pass