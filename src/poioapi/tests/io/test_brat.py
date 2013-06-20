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
                                "brat_graf", "dict-aleman2000-9-69.hdr")
        outputfile = os.path.join(os.path.dirname(__file__), "..", "sample_files",
                                  "brat_graf", "result")

        parser = graf.io.GraphParser()
        graph = parser.parse(filename)

        self.brat = poioapi.io.brat.Writer(graph, outputfile)

    def test_write(self):

        self.brat.write("dictinterpretation", feature_name="substring")

        annotations = os.path.join(os.path.dirname(__file__), "..", "sample_files",
                                   "brat_graf", "dict-aleman2000-9-69.ann")

        annotations_res = os.path.join(os.path.dirname(__file__), "..", "sample_files",
                                       "brat_graf", "result.ann")

        file_ann = open(annotations, "r")
        file_ann_res = open(annotations_res, "r")

        expect_lines = file_ann.readlines()
        result_lines = file_ann_res.readlines()

        assert file_ann.readlines() == file_ann_res.readlines()