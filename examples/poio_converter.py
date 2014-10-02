# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: Peter Bouda <pbouda@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

import sys
import optparse
import codecs
import os

import poioapi.annotationgraph
import poioapi.data
import poioapi.io.typecraft
import poioapi.io.latex


def main(argv):
    usage = "usage: %prog [options] inputfile outputfile"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-i", "--inputtype", dest="inputtype",
        help="Type of the input file (elan|toolbox|shoebox|mandinka|odin)")
    parser.add_option("-o", "--outputtype", dest="outputtype",
        help="Type of the output file (html|graf|typecraft|latex)")
    parser.add_option("-r", "--roottier", dest="roottier",
        help="Root tier for html output, is the record marker in Toolbox")
    parser.add_option("-t", "--map-file", dest="mapping",
                      help="A JSON file containing the tier and tag mapping.")
    parser.add_option("-m", "--missing-tags", action='store_true', dest="missing_tags", default=False,
                      help="If any missing tags are found, writes them to the output file, in JSON format. "
                           "If this flag is omitted, but missing tags are found, they are ignored.")
    parser.add_option('-l', '--language-code', dest='language_code', default='und',
                      help='The language of the source text. Use the ISO 639-3 code for the language as the value'
                           ' of this parameter.')
    (options, files) = parser.parse_args()

    if len(files) != 2:
        parser.print_usage()
        sys.exit(0)

    if options.inputtype not in ['toolbox', 'elan', 'shoebox', 'obt',
                                 'mandinka', 'odin']:
        parser.print_usage()
        sys.exit(0)

    if options.outputtype not in ['html', 'graf', 'typecraft', 'latex']:
        parser.print_usage()
        sys.exit(0)
    mapping = None
    if options.mapping:
            if os.path.exists(options.mapping):
                mapping = options.mapping
            else:
                print('The file {0} does not exist.'.format(options.mapping))
                parser.print_help()
                sys.exit(0)

    # Load the data from files
    ag = None
    if options.inputtype == "elan":
        ag = poioapi.annotationgraph.AnnotationGraph.from_elan(files[0])
    elif options.inputtype == "mandinka":
        ag = poioapi.annotationgraph.AnnotationGraph.from_mandinka(files[0])
    elif options.inputtype == "obt":
        ag = poioapi.annotationgraph.AnnotationGraph.from_obt(files[0])
    elif options.inputtype == "shoebox":
        ag = poioapi.annotationgraph.AnnotationGraph.from_shoebox(files[0])
    elif options.inputtype == "toolbox":
        if not options.roottier:
            print("No record marker specified (argument \"-r\"). Assuming \"ref\" as record marker.")

        ag = poioapi.annotationgraph.AnnotationGraph.from_toolbox(files[0])
    elif options.inputtype == 'odin':
        ag = poioapi.annotationgraph.AnnotationGraph.from_odin(files[0])


    # Set the structure type for hierarchical/interlinear output
    root_found = False
    if options.roottier:
        for th in ag.tier_hierarchies:
            if options.roottier == th[0] or th[0].endswith('..' + options.roottier):
                ag.structure_type_handler = poioapi.data.DataStructureType(th)
                root_found = True

    if not root_found:
        print("Could not find root tier in file or root tier was not specified. Will use the first tier hierarchy.")

    if options.outputtype == "html":
        # Output as html
        f = codecs.open(files[1], "w", "utf-8")
        f.write(ag.as_html_table(False, True))
        f.close()
    elif options.outputtype == "graf":
        writer = poioapi.io.graf.Writer()
        writer.write(files[1], ag)
    elif options.outputtype == "typecraft":
        missing_tags = options.missing_tags

        typecraft = poioapi.io.typecraft.Writer()
        if missing_tags:
            typecraft.missing_tags(files[1], ag, additional_map_path=mapping)
        else:
            typecraft.write(files[1], ag, extra_tag_map=mapping, language=options.language_code)
    elif options.outputtype == 'latex':
        latex = poioapi.io.latex.Writer()
        latex.write(files[1], ag)

if __name__ == "__main__":
    main(sys.argv)