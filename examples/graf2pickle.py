# -*- coding: utf-8 -*-
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT

import sys, getopt

from poioapi import annotationtree, data
from poioapi.io.graf import Parser

def main(argv):

    inputfile = ''
    outputfile = ''

    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('graf2pickle.py -i <inputfile> -o <outputfile>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('graf2pickle.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ('-i', '--ifile'):
            inputfile = arg
        elif opt in ('-o', '--ofile'):
            outputfile = arg

    if inputfile == "" or outputfile == "":
        print('graf2pickle.py -i <inputfile> -o <outputfile>')
        sys.exit()

    # Define data structure hierarchy
    data_hierarchy = data.DataStructureTypeGraid()

    # Create the annotation tree with the created data structure
    annotation_tree = annotationtree.AnnotationTree(data_hierarchy)

    parser = Parser(annotation_tree, inputfile)

    annotation_tree = parser.load_as_tree()

    annotation_tree.save_tree_as_pickle(outputfile)

    print('Finished')

if __name__ == "__main__":
    main(sys.argv[1:])