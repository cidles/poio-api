# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

import os

import poioapi.io.toolbox
import poioapi.io.graf

class TestToolboxLine:

    def setup(self):
        self.line = "\mb diž y-   ike -s   .     diž b-   ike -s   čeq  čeq  -i      rekʼe"
        self.toolbox_line = poioapi.io.toolbox.ToolboxLine(self.line)

    def test_char_len(self):
     	assert poioapi.io.toolbox.ToolboxLine.char_len(self.line) == 70

    def test_line_string(self):
     	assert self.toolbox_line.line_original == self.toolbox_line.line_string

class TestToolbox:
    """
    This class contain the test methods to the
    class io.toolbox.py.

    """

    def setup(self):
        self.filename = os.path.join(os.path.dirname(__file__), "..",
        	"sample_files", "toolbox_graf", "toolbox.txt")

        self.parser = poioapi.io.toolbox.Parser(self.filename)

