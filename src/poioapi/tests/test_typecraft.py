# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

import os

from poioapi.io import typecraft

class TestTypecraft:
    """
    This class contain the test methods to the
    class io.typecraft.py.

    """

    def setup(self):
        self.filename = os.path.join(os.path.dirname(__file__), "sample_files",
            "typecraft_graf", "typecraft_example.eaf")

        self.basedirname = os.path.dirname(self.filename)

        self.typecraft = typecraft.Typecraft(self.filename)