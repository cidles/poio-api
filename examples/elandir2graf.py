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
from poioapi.io import elan

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

    for file in os.listdir(inputdir):
        (basedirname, _) = os.path.splitext(file)
        inputfile = inputdir+file

        # Initialize
        elan_graf = elan.Elan(inputfile)

        # Create a GrAF object
        graph = elan_graf.as_graf()

        # Create GrAF Xml files
        elan_graf.generate_graf_files()

        inputfile = inputdir+basedirname+"-extinfo.xml"
        outputfile = inputdir+basedirname+"_result.eaf"

        # Initialize
        elan_write = elan.ElanWriter(inputfile, outputfile)

        # Write the Elan file
        elan_write.write_elan()

    print('Finished')

if __name__ == "__main__":
    main(sys.argv[1:])