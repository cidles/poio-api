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

import graf


class TestBrat:
    """
    This class contain the test methods to the
    class io.brat.py.

    """

    def setup(self):
        filename = os.path.join(os.path.dirname(__file__), "..", "sample_files",
                                "brat", "text.hdr")
        outputfile = os.path.join(os.path.dirname(__file__), "..", "sample_files",
                                "brat", "result_text")

        parser = graf.io.GraphParser()
        graph = parser.parse(filename)

        self.brat = poioapi.io.brat.Writer(graph, outputfile)

    def test_write(self):

        self.brat.write()

        annotation_conf = os.path.join(os.path.dirname(__file__), "..", "sample_files",
                                       "brat", "annotation.conf")

        annotation_conf_res = os.path.join(os.path.dirname(__file__), "..", "sample_files",
                                           "brat", "annotation.conf")

        assert annotation_conf == annotation_conf_res