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
import sys
import pickle
import codecs

from poioapi import annotationtree
from poioapi import data
from poioapi.io import graf

def main(argv):
    if len(argv) < 3:
        print("call: pickle2graf.py pickle_file graf_header_file")
        exit(1)


    # Pickle file path
    pickle_file = argv[1]
    graf_header_file = argv[2]

    # Create the data structure
    data_hierarchy = data.DataStructureTypeGraid()

    # Create the annotation tree with the created data structure
    annotation_tree = annotationtree.AnnotationTree(data_hierarchy)

    # Open the file
    annotation_tree.load_tree_from_pickle(pickle_file)

    # Call the writer to GrAF
    graf.Writer(annotation_tree, graf_header_file).write()


if __name__ == "__main__":
    main(sys.argv)