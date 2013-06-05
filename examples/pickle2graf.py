# -*- coding: utf-8 -*-
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT

import os
import sys
import getopt

import poioapi.annotationgraph
import poioapi.data

def main(argv):

    inputfile = ''
    outputfile = ''

    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('pickle2graf.py -i <inputfile> -o <outputfile>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('pickle2graf.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ('-i', '--ifile'):
            inputfile = arg
        elif opt in ('-o', '--ofile'):
            outputfile = arg

    if inputfile == "" or outputfile == "":
        print('pickle2graf.py -i <inputfile> -o <outputfile>')
        sys.exit()

    # Initialize the annotation graph
    annotation_graph = poioapi.annotationgraph.AnnotationGraph(None)

    # Create a graph from an pickle file
    annotation_graph.from_pickle(inputfile)

    graf_graph = annotation_graph.graf
    tier_hierarchies = annotation_graph.tier_hierarchies

    writer = poioapi.io.graf.Writer()

    # Set values for the document header
    writer.standoffheader.filedesc.titlestmt = "Pickle Example"
    writer.standoffheader.datadesc.primaryData = {'loc': os.path.basename(inputfile),
                                                  'f.id': "text"}

    writer.write(outputfile, graf_graph, tier_hierarchies)

    print('Finished')

if __name__ == "__main__":
    main(sys.argv[1:])


