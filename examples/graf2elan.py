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
import poioapi.io.elan

def main(argv):

    inputfile = ''
    outputfile = ''

    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('graf2elan.py -i <inputfile> -o <outputfile>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('graf2elan.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ('-i', '--ifile'):
            inputfile = arg
        elif opt in ('-o', '--ofile'):
            outputfile = arg

    if inputfile == "" or outputfile == "":
        print('graf2elan.py -i <inputfile> -o <outputfile>')
        sys.exit()

    # Create the data structure
    data_hierarchy = None

    # Initialize the annotation graph
    annotation_graph = poioapi.annotationgraph.AnnotationGraph(data_hierarchy)

    # Create a graph from an elan file
    annotation_graph.from_elan(inputfile)

    graf_graph = annotation_graph.graf
    tier_hierarchies = annotation_graph.tier_hierarchies
    meta_information = annotation_graph.meta_information
    primary_data = annotation_graph.primary_data

    # Initialize
    elan = poioapi.io.elan.Writer()

    # Write the Elan file
    elan.write(outputfile, graf_graph, tier_hierarchies, primary_data, meta_information)

    print('Finished')

if __name__ == "__main__":
    main(sys.argv[1:])