# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
""" This module is to create the raw txt
file form the pickle file
"""
from xml.dom.minidom import Document
from poioapi import annotationtree
from poioapi import data

import codecs
import os
import pickle

class CreateRawFile:

    def __init__(self, filepath):
        self.filepath = filepath

    def create_raw_file(self):
        # Initialize the variable
        annotation_tree = annotationtree.AnnotationTree(data.GLOSS)

        # Open the file
        file = open(self.filepath, "rb")
        annotation_tree.tree = pickle.load(file)

        # Start the txt file
        basename = self.filepath.split('.pickle')
        file = os.path.abspath(basename[0] + '.txt')
        f = codecs.open(file,'w', 'utf-8') # Need the encode

        # Verify the elements
        for element in annotation_tree.elements():

            # Get the utterance
            utterance = element[0]

            # Write the content to the txt file
            f.write(utterance.get('annotation') + '\n')

        # Close txt file
        f.close()

        self.create_raw_seg()

    def create_raw_seg(self):
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
        last_counter = 0

        # Start XML file
        basename = self.filepath.split('.pickle')
        file = os.path.abspath(basename[0] + '-utt.xml')
        f = codecs.open(file,'w','utf-8')

        # Verify the elements
        for element in annotation_tree.elements():

            # Get the utterance
            utterance = element[0]

            counter = last_counter

            last_counter += len(utterance.get('annotation'))

            region = doc.createElement("region")
            region.setAttribute("xml:id", "utt-r"
            + str(seg_count)) # Region
            region.setAttribute("anchors",
                str(counter) + " " +
                str(last_counter)) # Anchors

            graph.appendChild(region)

            seg_count+=1

        # Write the content in XML file
        f.write(doc.toprettyxml(indent="  "))

        #Close XML file
        f.close()