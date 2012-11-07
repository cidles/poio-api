# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
""" This document is an example of the creation of
GrAF files.
"""

from poioapi import data
from poioapi.io import graf

# Pickle file path
# The file should be generated first with the parser
headerfile = 'Example-header.hdr'

# Creates a list of nodes, their values and their dependencies
graf.Render(headerfile).load(data.DataStructureTypeGraid().data_hierarchy)

# Generate a rendered file with all the nodes
graf.Render(headerfile).generate_file()
