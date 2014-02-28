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

import poioapi.annotationgraph
import poioapi.data
import poioapi.io.typecraft


def main(argv):
    usage = "usage: %prog [options] inputfile outputfile"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-i", "--inputtype", dest="inputtype",
        help="Type of the input file (elan|toolbox|shoebox)")
    parser.add_option("-o", "--outputtype", dest="outputtype",
        help="Type of the output file (html|graf|typecraft)")
    parser.add_option("-r", "--roottier", dest="roottier",
        help="Root tier for html output, is the record marker in Toolbox")
    parser.add_option("-t", "--tags", dest="tags",
        help="Tag set")
    parser.add_option("-m", "--more", dest="more",
        help="Add extra information")
    (options, files) = parser.parse_args()

    if len(files) != 2:
        parser.print_usage()
        sys.exit(0)

    if options.inputtype not in ['toolbox', 'elan', 'shoebox', 'obt']:
        parser.print_usage()
        sys.exit(0)

    if options.outputtype not in ['html', 'graf', 'typecraft']:
        parser.print_usage()
        sys.exit(0)

    # Create an empty annotation graph
    ag = poioapi.annotationgraph.AnnotationGraph(None)

    # Load the data from EAF file
    if options.inputtype == "elan":
        ag.from_elan(files[0])
    elif options.inputtype == "obt":
        ag.from_obt(files[0])
    elif options.inputtype == "shoebox":
        ag.from_shoebox(files[0])
    elif options.inputtype == "toolbox":
        if not options.roottier:
            print("No record marker specified (argument \"-r\"). Assuming \"ref\" as record marker.")

        ag.from_toolbox(files[0])

    # Set the structure type for hierarchical/interlinear output
    root_found = False
    if options.roottier:
        for th in ag.tier_hierarchies:
            if options.roottier == th[0] or th[0].endswith('..' + options.roottier):
                ag.structure_type_handler = poioapi.data.DataStructureType(th)
                root_found = True

    if not root_found:
        print("Could not find root tier in file or root tier was not specified. Will use the first tier hierarchy.")
        ag.structure_type_handler = poioapi.data.DataStructureType(ag.tier_hierarchies[0])

    if options.outputtype == "html":
        # Output as html
        f = codecs.open(files[1], "w", "utf-8")
        f.write(ag.as_html_table(False, True))
        f.close()
    elif options.outputtype == "graf":
        writer = poioapi.io.graf.Writer()
        writer.write(files[1], ag)
    elif options.outputtype == "typecraft":
        more_info = None
        tags = None

        if options.more:
            more_info = options.more
        if options.tags:
            tags = options.tags

        typecraft = poioapi.io.typecraft.Writer()
        typecraft.write(files[1], ag, more_info=more_info, tags=tags)

if __name__ == "__main__":
    main(sys.argv)