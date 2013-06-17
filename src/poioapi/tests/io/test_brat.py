# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

from __future__ import absolute_import

import os

import poioapi.io.brat
import poioapi.io.elan
import poioapi.io.graf
import poioapi.io.toolbox

import graf

class TestBrat:
    """
    This class contain the test methods to the
    class io.brat.py.

    """

    def setup(self):
        # self.filename = os.path.join(os.path.dirname(__file__), "..", "sample_files",
        #                              "elan_graf", "example.eaf")


        # parser = poioapi.io.elan.Parser(self.filename)
        # converter = poioapi.io.graf.GrAFConverter(parser)
        # converter.parse()
        #
        # self.graph = converter.graf

        parser = graf.io.GraphParser()
        self.graph = parser.parse(filename)

        self.brat = poioapi.io.brat.Writer(self.graph)

    def test_write(self):

        self.brat.write(None)

        for node in self.graf.nodes:
            pass

        assert 1 == 2