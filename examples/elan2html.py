# -*- coding: utf-8 -*-
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT

import sys
import codecs
import getopt

import poioapi.annotationgraph
import poioapi.data

# This class describes the data structure in the example file in
# "example_data/turkish.eaf"
class DataStructureTypeElan(poioapi.data.DataStructureType):
     name = "ELAN"

     data_hierarchy = \
     [ 'Äußerung',
         [ 'Wort',
             [ 'Morphem',
                 [ 'Glosse' ],
             ]
         ],
       'Übersetzung']


# This class describes the data structure in the example file in
# "example_data/example.eaf"
# taken from: http://www.mpi.nl/tools/elan/elan-example.zip
#class DataStructureTypeElan(poioapi.data.DataStructureType):
#    name = "ELAN"
#
#    data_hierarchy = \
#    [ 'utterance/W-Spch',
#        [ 'words/W-Words',
#          'part_of_speech/W-POS'
#        ],
#      'phonetic_transcription/W-IPA'
#    ]


def main(argv):
    inputfile = ''
    outputfile = ''

    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
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

    data_structure = DataStructureTypeElan()

    annotation_graph = poioapi.annotationgraph.AnnotationGraph(data_structure)
    annotation_graph.from_elan(inputfile)

    html = annotation_graph.as_html_table()

    f = codecs.open(outputfile, "w", "utf-8")
    f.write(html)
    f.close()

if __name__ == "__main__":
    main(sys.argv[1:])