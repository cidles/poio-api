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

import poioapi.io.graf
import poioapi.io.tcf


def main(argv):
    inputfile = ''
    outputfile = ''

    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print('tcf2graf.py -i <inputfile> -o <outputfile>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('tcf2graf.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ('-i', '--ifile'):
            inputfile = arg
        elif opt in ('-o', '--ofile'):
            outputfile = arg

    if inputfile == "" or outputfile == "":
        print('tcf2graf.py -i <inputfile> -o <outputfile>')
        sys.exit()

    parser = poioapi.io.tcf.Parser(inputfile)

    converter = poioapi.io.graf.GrAFConverter(parser)
    converter.parse()

    graf_graph = converter.graf
    tier_hierarchies = converter.tier_hierarchies
    meta_information = converter.meta_information
    primary_data = converter.primary_data

    writer = poioapi.io.graf.Writer()

    # Set values for the document header
    writer.standoffheader.filedesc.titlestmt = "TCF Example"
    writer.standoffheader.profiledesc.catRef = "EN"
    writer.standoffheader.filedesc.documentation = "Documentation Place"

    writer.write(outputfile, graf_graph, tier_hierarchies, primary_data, meta_information)

    print('Finished')

if __name__ == "__main__":
    main(sys.argv[1:])
