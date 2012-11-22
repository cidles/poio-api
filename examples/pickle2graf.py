# -*- coding: utf-8 -*-
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT

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



