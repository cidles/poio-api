# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
""" This module is to test all the parsing modules
and methods that PoioAPI parser uses. Including the
parser to the three data hierarchies, GRAID,
MORPHSYN and WORD.

Note: This module it'll test the modules that
generates a XML file.
"""

import os
import comment

class TestCreateCommentFile:
    """
    This class contain the test methods to the
    class comment.py.

    """

    def test_create_cmts_xml(self):
        """Raise an assertion if can't retrieve the file.

        Return given file(s) as a single string.

        Raises
        ------
        AssertionError
            If can't retrieve a string.

        """

        # Initialize values
        filepath = '/home/alopes/tests/pi_2.pickle'

        comment.CreateCommentFile(filepath).create_cmts_xml()

        # The result must be pi_2-cmt.pickle because of the
        # create_cmts_xml it'll add the sufix -cmt to the
        # original file name.

        # Open the file
        basename = filepath.split('.pickle')
        file = os.path.abspath(basename[0] + '-cmt.xml')
        xml_file = open(file, 'r')

        # Getting the xml content
        xml_content = xml_file.readlines()

        xml_file.close()

        # Opening the expected file result
        file = os.path.abspath('comment-xml')
        xml_file = open(file, 'r')

        # Getting the xml content
        expected_result = xml_file.readlines()

        xml_file.close()

        assert(xml_content == expected_result)


