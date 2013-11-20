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

from __future__ import absolute_import

import re

import xml.etree.ElementTree as ET

import poioapi.io.graf


class Parser(poioapi.io.graf.BaseParser):

    def __init__(self, filepath):
        """Class's constructor.

        Parameters
        ----------
        filepath : str
            Path of the Toolbox TXT file.

        """

        self.filepath = filepath
        self.parse()

    def parse(self):
        """This method will parse the input file.

        """

        pass