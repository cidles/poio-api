# -*- coding: utf-8 -*-
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

import sys, getopt

from poioapi.io import elan

def main(argv):

    inputfile = ''
    outputfile = ''

    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('graf2elan.py -i <inputfile> -o <outputfile>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('graf2elan.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ('-i', '--ifile'):
            inputfile = arg
        elif opt in ('-o', '--ofile'):
            outputfile = arg

    if inputfile == "" or outputfile == "":
        print('graf2elan.py -i <inputfile> -o <outputfile>')
        sys.exit()

    # Initialize
    elan_write = elan.ElanWriter(inputfile, outputfile)

    # Write the Elan file
    elan_write.write()

    print('Finished')

if __name__ == "__main__":
    main(sys.argv[1:])