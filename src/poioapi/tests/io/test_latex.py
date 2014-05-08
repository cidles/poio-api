# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2014 Poio Project
# Author: Pedro Manha <pmanha@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

import poioapi.io.latex
import poioapi.annotationgraph

import os.path
import filecmp


class TestWriter():

    def test_write_with_mandinka(self):
        input = os.path.join(os.path.dirname(__file__), "..",
            "sample_files", "mandinka", "mandinka_latex.txt")

        output = os.path.join(os.path.dirname(__file__), "..",
            "sample_files", "latex", "mandinka_latex.tex")

        expected = os.path.join(os.path.dirname(__file__), "..",
            "sample_files", "latex", "mandinka_latex_expected.tex")

        ag = poioapi.annotationgraph.AnnotationGraph()
        ag = ag.from_mandinka(input)
        writer = poioapi.io.latex.Writer()
        writer.write(output, ag)

        assert(os.path.getsize(output) == os.path.getsize(expected))
        assert(filecmp.cmp(output, expected, False))

    def test_write_with_toolbox(self):
        input = os.path.join(os.path.dirname(__file__), "..",
            "sample_files", "toolbox_graf", "toolbox_latex.txt")

        output = os.path.join(os.path.dirname(__file__), "..",
            "sample_files", "latex", "toolbox_latex.tex")

        expected = os.path.join(os.path.dirname(__file__), "..",
            "sample_files", "latex", "toolbox_latex_expected.tex")

        ag = poioapi.annotationgraph.AnnotationGraph()
        ag = ag.from_toolbox(input)
        writer = poioapi.io.latex.Writer()
        writer.write(output, ag)

        assert(os.path.getsize(output) == os.path.getsize(expected))
        assert(filecmp.cmp(output, expected, False))