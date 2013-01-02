# -*- coding: utf-8 -*-
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT

import sys, getopt

import poioapi.io.elan

def main(argv):

    inputfile = ''
    outputfile = ''

    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('elan2graf.py -i <inputfile> -o <outputfile>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('elan2graf.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ('-i', '--ifile'):
            inputfile = arg
        elif opt in ('-o', '--ofile'):
            outputfile = arg

    if inputfile == "" or outputfile == "":
        print('elan2graf.py -i <inputfile> -o <outputfile>')
        sys.exit()

    elan_graf = poioapi.io.elan.ElanToGraf(inputfile)

    # Create a GrAF object
    graph = elan_graf.elan_to_graf()

    # Create GrAF Xml files
    elan_graf._create_graf_files()

    # Rendering the GrAF object to an Xml file
    elan_graf.graph_rendering(outputfile, graph)

    # Header file
    header_file = elan_graf.header

    # Data Structure hierarchy
    data_structure_hierarchy = elan_graf.data_structure_hierarchy

    # Generate a metafile with the necessary data
    elan_graf.generate_metafile(graph, header_file, data_structure_hierarchy,
        outputfile)

    print('Finished')

if __name__ == "__main__":
    main(sys.argv[1:])