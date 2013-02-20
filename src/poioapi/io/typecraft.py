# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT
"""This module contains classes to access to
Typecraf files.
"""

import os

from xml.etree.ElementTree import Element, SubElement, tostring
import xml.etree.ElementTree as ET

class Typecraft:
    """
    Class that will handle the parse of
    Typecraft files.

    """

    def __init__(self, filepath):
        """Class's constructor.

        Parameters
        ----------
        filepath : str
            Path of the elan file.

        """

        self.filename = os.path.basename(filepath)
        self.filepath = filepath

    def parser(self):
        tree = ET.parse(self.filepath)
        doc = tree.getroot()