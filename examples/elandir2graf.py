# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

import os
import sys
import getopt

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

        # Create a graph from an elan file
        annotation_graph.from_elan(inputfile)

        graf_graph = annotation_graph.graf
        tier_hierarchies = annotation_graph.tier_hierarchies
        meta_information = annotation_graph.meta_information

        writer = poioapi.io.graf.Writer()

        # Set values for the document header
        writer.standoffheader.filedesc.titlestmt = "Elan File"
        writer.standoffheader.datadesc.primaryData = {'loc': os.path.basename(inputfile),
                                                      'f.id': "audio"}

        outputfile = inputdir+basedirname+".hdr"
        writer.write(outputfile, graf_graph, tier_hierarchies, meta_information)

        # Initialize
        elan = poioapi.io.elan.Writer()

        outputfile = inputdir+basedirname+"_new.eaf"

        # Write back the Elan file
        elan.write(outputfile, graf_graph, tier_hierarchies, meta_information)

    print('Finished')

if __name__ == "__main__":
    main(sys.argv[1:])