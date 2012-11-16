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

from poioapi import data
from poioapi.io import graf

# Pickle file path
# The file should be generated first with the parser
headerfile = 'Example-header.hdr'

# Create an annotation tree from the header file
annotation_tree = graf.Render(headerfile).\
load_as_tree(data.DataStructureTypeGraid().data_hierarchy)

# Consulting the elements
for element in annotation_tree.elements():
    print(element)
    print("\n")

# Generate a rendered file with all the nodes
graf.Render(headerfile).generate_file()
