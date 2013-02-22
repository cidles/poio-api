# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

import sys, getopt

from poioapi.io import typecraft

def main(argv):

    inputfile = ''

    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile="])
    except getopt.GetoptError:
        print('typecraft2graf.py -i <inputfile>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('typecraft2graf.py -i <inputfile>')
            sys.exit()
        elif opt in ('-i', '--ifile'):
            inputfile = arg

    if inputfile == "":
        print('typecraft2graf.py -i <inputfile>')
        sys.exit()

    # Initialize
    typecraft_graf = typecraft.Typecraft(inputfile)

    # Create a GrAF object
    graph = typecraft_graf.typecraft_to_elan()

    # Generate the files
    typecraft_graf.generate_graf_files()

    print('Finished')

if __name__ == "__main__":
    main(sys.argv[1:])