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
import poioapi.io.graf


def main(argv):
    inputfile = ''
    outputfile = ''

    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print('toolbox2graf.py -i <inputfile> -o <outputfile>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('toolbox2graf.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ('-i', '--ifile'):
            inputfile = arg
        elif opt in ('-o', '--ofile'):
            outputfile = arg

    if inputfile == "" or outputfile == "":
        print('toolbox2graf.py -i <inputfile> -o <outputfile>')
        sys.exit()

    # Create the data structure
    data_hierarchy = None

    # Initialize the annotation graph
    annotation_graph = poioapi.annotationgraph.AnnotationGraph(data_hierarchy)

    # Create a graph from an elan file
    annotation_graph.from_toolbox(inputfile)

    graf_graph = annotation_graph.graf
    tier_hierarchies = annotation_graph.tier_hierarchies

    writer = poioapi.io.graf.Writer()

    # Set values for the document header
    writer.standoffheader.filedesc.titlestmt = "Toolbox XML Example"
    writer.standoffheader.profiledesc.catRef = "EN"
    writer.standoffheader.filedesc.documentation = "Documentation Place"
    writer.standoffheader.datadesc.primaryData = {'loc': os.path.basename(inputfile),
                                                  'f.id': "text"}

    writer.write(outputfile, graf_graph, tier_hierarchies)

    print('Finished')

if __name__ == "__main__":
    main(sys.argv[1:])