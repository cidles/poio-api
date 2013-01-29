# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: Peter Bouda <pbouda@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

import sys
import codecs
import getopt

import poioapi.annotationgraph
import poioapi.data

class DataStructureTypeElan(poioapi.data.DataStructureType):
    name = "ELAN"

    data_hierarchy =\
    [ 'utterance', 'phonetic_transcription',
        [ 'words', 'part_of_speech' ]
    ]


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
            print('graf2html.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ('-i', '--ifile'):
            inputfile = arg
        elif opt in ('-o', '--ofile'):
            outputfile = arg

    if inputfile == "" or outputfile == "":
        print('graf2html.py -i <inputfile> -o <outputfile>')
        sys.exit()

    # Create the data structure
    data_hierarchy = poioapi.data.GRAID

    # Create the annotation tree with the created data structure
    annotation_graph = poioapi.annotationgraph.AnnotationGraph(data_hierarchy)
    annotation_graph.structure_type_handler = DataStructureTypeElan()

    # Open the file
    annotation_graph.load_graph_from_graf(inputfile)
    html = annotation_graph.as_html_table(full_html = True)

    f = codecs.open(outputfile, "w", "utf-8")
    f.write(html)
    f.close()

    print('Finished')

if __name__ == "__main__":
    main(sys.argv[1:])


