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
import codecs

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

        self.outputfile = os.path.join(os.path.dirname(__file__), "..", "sample_files",
                                       "brat_graf", "result.ann")

        parser = graf.io.GraphParser()
        self.graph = parser.parse(filename)

        self.brat = poioapi.io.brat.Writer("dictinterpretation", "substring")

    def test_write(self):

        self.brat.write(self.outputfile, self.graph)

        annotations = os.path.join(os.path.dirname(__file__), "..", "sample_files",
                                   "brat_graf", "dict-aleman2000-9-69.ann")

        annotations_res = os.path.join(os.path.dirname(__file__), "..", "sample_files",
                                       "brat_graf", "result.ann")

        file_ann = codecs.open(annotations, "r", "utf-8")
        file_ann_res = codecs.open(annotations_res, "r", "utf-8")

        assert len(file_ann.readlines()) == len(file_ann_res.readlines())