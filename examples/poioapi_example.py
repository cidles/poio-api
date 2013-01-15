# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT
"""This module contains a simple example 
how to use the PoioAPI and retrieve
some of the elements of an 
AnnotationTree.
"""

import pickle

from poioapi import annotationtree
from poioapi import data

# Initialize the variable
annotation_tree = annotationtree.AnnotationTree(data.GLOSS)

# Open the file
file = open('Balochi Text1.pickle', "rb")
annotation_tree.tree = pickle.load(file)

# Verify the elements
for element in annotation_tree.elements():
    print(element)
    print("\n")