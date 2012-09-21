# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
""" This module is to create the regions
of the WFW one by one
"""
from xml.dom.minidom import Document
from poioapi import annotationtree
from poioapi import data

import os
import pickle
import codecs

class CreateSegWFW:

    def __init__(self, filepath):
        self.filepath = filepath

    def create_wfw_file(self):

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
        file = os.path.abspath('/home/alopes/tests/seg-wfw.xml')
        f = open(file,'w')

        # Verify the elements
        for element in annotation_tree.elements():

            # Get the utterance
            utterance = element[1]

            for wfw_el in utterance:
                for el in wfw_el[1]:
                    st = el[1].get('annotation')

                    for char in st:
                        counter+=1

                        if char == ' ':
                            region = doc.createElement("region")
                            region.setAttribute("xml:id", "seg-r"
                            + str(seg_count)) # Region
                            region.setAttribute("anchors",
                                str(last_counter) + " " +
                                str(counter - 1)) # Anchors

                            graph.appendChild(region)

                            # Update the last_counter
                            last_counter = counter

                            seg_count+=1

                    region = doc.createElement("region")
                    region.setAttribute("xml:id", "seg-r" +
                                                  str(seg_count)) # Region
                    region.setAttribute("anchors",
                        str(last_counter) + " " + str(counter)) # Anchors

                    graph.appendChild(region)

                    # Update the last_counter
                    last_counter = counter

                    seg_count+=1

        # Write the content in XML file
        f.write(doc.toprettyxml(indent="  "))

        #Close XML file
        f.close()

        # Is need to create a raw file with the
        # right content
        self.create_raw_file()

    def create_raw_file(self):
        # Initialize the variable
        annotation_tree = annotationtree.AnnotationTree(data.GLOSS)

        # Open the file
        file = open(self.filepath, "rb")
        annotation_tree.tree = pickle.load(file)

        # Start XML file
        file = os.path.abspath('/home/alopes/tests/wfw_raw.txt')
        f = codecs.open(file,'w', 'utf-8') # Need the encode

        id_counter = 0

        # Verify the elements
        for element in annotation_tree.elements():

            # Get the utterance
            utterance = element[1]

            for wfw_el in utterance:
                id_counter+=1
                for el in wfw_el[1]:
                    st = el[1].get('annotation')
                    # Write the content to the txt file
                    f.write(st + '[id:'+ str(id_counter) + ']\n')

        # Close txt file
        f.close()