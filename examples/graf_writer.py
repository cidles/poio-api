# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
""" This document is an example of the creation of
GrAF files.
"""
from poioapi import annotationtree
from poioapi import data
from poioapi.io import graf

import pickle

# Pickle file path
filepath = 'Example.pickle'

# Create the data structure
data_hierarchy = data.DataStructureTypeGraid()

# Create the annotation tree with the created data structure
annotation_tree = annotationtree.AnnotationTree(data_hierarchy)

# Open the file
file = open(filepath, "rb")
annotation_tree.tree = pickle.load(file)

# Header file
headerfile = 'Example-header.hdr'

# Call the writer to GrAF
graf.Writer(annotation_tree, headerfile).write()
