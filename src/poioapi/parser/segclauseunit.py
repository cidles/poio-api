# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
""" This document is to create the regions
of the words in the clause units one by one
"""

from xml.dom.minidom import Document
from poioapi import annotationtree
from poioapi import data

import os
import pickle

class CreateSegClauseUnits:

    def __init__(self, filepath):
        self.filepath = filepath

    def create_clause_units_file(self):

        # Initialize the variable
        annotation_tree = annotationtree.AnnotationTree(data.GLOSS)

        # Open the file
        file = open(self.filepath, "rb")
        annotation_tree.tree = pickle.load(file)

        doc = Document()
        graph = doc.createElement("graph")
        graph.setAttribute("xmlns:graf", "http://www.xces.org/ns/GrAF/1.0/")
        doc.appendChild(graph)

        # Not need for this seg
        graphheader = doc.createElement("graphHeader")
        labelsdecl = doc.createElement("labelsDecl")
        graphheader.appendChild(labelsdecl)
        graph.appendChild(graphheader)

        # Auxiliary variables
        seg_count = 0
        counter = 0
        last_counter = 0
        words = []

        # Start XML file
        file = os.path.abspath('/home/alopes/tests/seg-clause.xml')
        f = open(file,'w')

        # Verify the elements
        for element in annotation_tree.elements():

            # Get the clause unit
            clause_units = element[1]
            i = 0

            # Get the clause units
            while i < int(len(clause_units)):
                clause_unit = clause_units[i]
                for char in clause_unit[0].get('annotation'):
                    counter+=1

                region = doc.createElement("region")
                region.setAttribute("xml:id", "seg-r" + str(seg_count)) # Region
                region.setAttribute("anchors",
                    str(last_counter) + " " + str(counter + 1)) # Anchors

                graph.appendChild(region)

                # Update the last_counter
                last_counter = counter + 1

                seg_count+=1

                i+=1

        # Write the content in XML file
        f.write(doc.toprettyxml(indent="  "))

        #Close XML file
        f.close()