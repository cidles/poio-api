# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

import os
import sys, getopt

import poioapi.annotationgraph
import poioapi.io.elan

def main(argv):

    inputdir = ''

    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile="])
    except getopt.GetoptError:
        print('elandir2graf.py -i <inputdir> ')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('elandir2graf.py -i <inputdir>')
            sys.exit()
        elif opt in ('-i', '--idirectory'):
            inputdir = arg

    if inputdir == "":
        print('elandir2graf.py -i <inputdir>')
        sys.exit()

    # Create the data structure
    data_hierarchy = None

    # Initialize the annotation graph
    annotation_graph = poioapi.annotationgraph.AnnotationGraph(data_hierarchy)

    for file in os.listdir(inputdir):
        (basedirname, _) = os.path.splitext(file)
        inputfile = inputdir+file

        print(inputfile)
        # Create a graph from an elan file
        annotation_graph.from_elan(inputfile)

        # Generate the GrAF files
        annotation_graph.generate_graf_files(inputfile, inputfile)

        inputfile = inputdir+basedirname+"-extinfo.xml"
        outputfile = inputdir+basedirname+"_result.eaf"

        # Initialize
        elan = poioapi.io.elan.Writer(inputfile, outputfile)

        # Write the Elan file
        elan.write()

    print('Finished')

if __name__ == "__main__":
    main(sys.argv[1:])