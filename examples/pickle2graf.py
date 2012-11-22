# -*- coding: utf-8 -*-
<<<<<<< HEAD
#
=======
>>>>>>> develop
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
<<<<<<< HEAD
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
=======

import sys, getopt

from poioapi import data, annotationtree
from poioapi.io.graf import Writer

def main(argv):

    inputfile = ''

    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile="])
    except getopt.GetoptError:
        print('pickle2graf.py -i <inputfile>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('pickle2graf.py -i <inputfile>')
            sys.exit()
        elif opt in ('-i', '--ifile'):
            inputfile = arg

            # Create the data structure
            data_hierarchy = data.DataStructureTypeGraid()

            # Create the annotation tree with the created data structure
            annotation_tree = annotationtree.AnnotationTree(data_hierarchy)

            # Open the file
            annotation_tree.load_tree_from_pickle(inputfile)

            # Once not all the existing files have
            # the regions is important to force it.
            # Or else the writer doesn't work properly.

            search_tier = 'utterance'
            update_tiers = ['clause unit', 'word']

            annotation_tree.update_elements_with_ranges(search_tier,
                update_tiers)
            annotation_tree.save_tree_as_pickle(inputfile)

            writer = Writer(annotation_tree, inputfile)

            # Write the GrAF files
            writer.write()

            print('Finished')

if __name__ == "__main__":
    main(sys.argv[1:])



>>>>>>> develop
