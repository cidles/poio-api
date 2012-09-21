# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
""" This module is to create the raw txt
file form the pickle file
"""

from poioapi import annotationtree
from poioapi import data

import codecs
import os
import pickle

class CreateRawFile:

    def __init__(self, filepath):
        self.filepath = filepath

    def create_raw_file(self):
        # Initialize the variable
        annotation_tree = annotationtree.AnnotationTree(data.GLOSS)

        # Open the file
        file = open(self.filepath, "rb")
        annotation_tree.tree = pickle.load(file)

        # Start XML file
        file = os.path.abspath('/home/alopes/tests/raw.txt')
        f = codecs.open(file,'w', 'utf-8') # Need the encode

        # Verify the elements
        for element in annotation_tree.elements():

            # Get the utterance
            utterance = element[0]

            # Write the content to the txt file
            f.write(utterance.get('annotation') + '\n')

        # Close txt file
        f.close()