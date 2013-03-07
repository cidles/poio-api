# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

import sys, getopt

import poioapi.annotationgraph
import poioapi.data

def main(argv):

    inputfile = ''

    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile="])
    except getopt.GetoptError:
        print('typecraft2graf.py -i <inputfile>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('typecraft2graf.py -i <inputfile>')
            sys.exit()
        elif opt in ('-i', '--ifile'):
            inputfile = arg

    if inputfile == "":
        print('typecraft2graf.py -i <inputfile>')
        sys.exit()

    # Create the data structure
    data_hierarchy = None

    # Initialize the annotation graph
    annotation_graph = poioapi.annotationgraph.AnnotationGraph(data_hierarchy)

    # Create a graph from an typecraft file
    annotation_graph.from_typecraft(inputfile)

    # Generate the GrAF files
    annotation_graph.generate_graf_files()

    print('Finished')

if __name__ == "__main__":
    main(sys.argv[1:])