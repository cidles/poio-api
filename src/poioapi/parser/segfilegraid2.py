# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
""" This module is to create the regions
of the GRAID 2
"""
from xml.dom.minidom import Document
from poioapi import annotationtree
from poioapi import data

import os
import pickle
import codecs

class Creategraid2File:

    def __init__(self, filepath):
        self.filepath = filepath

    def create_graid2_xml(self):

        # Initialize the variable
        annotation_tree = annotationtree.AnnotationTree(data.GLOSS)

        # Open the file
        file = open(self.filepath, "rb")
        annotation_tree.tree = pickle.load(file)

        doc = Document()
        graph = doc.createElement("graph")
        graph.setAttribute("xmlns:graf", "http://www.xces.org/ns/GrAF/1.0/")
        doc.appendChild(graph)

        # Header
        graphheader = doc.createElement("graphHeader")
        labelsdecl = doc.createElement("labelsDecl")
        graphheader.appendChild(labelsdecl)
        graph.appendChild(graphheader)

        dependencies = doc.createElement('dependencies')
        dependson = doc.createElement('dependsOn')
        dependson.setAttribute('f.id','clause')
        dependencies.appendChild(dependson)
        graphheader.appendChild(dependencies)

        ann_spaces = doc.createElement('annotationSpaces')
        ann_space = doc.createElement('annotationSpace')
        ann_space.setAttribute('as.id','graid2')
        ann_spaces.appendChild(ann_space)
        graphheader.appendChild(ann_spaces)

        # Start XML file
        basename = self.filepath.split('.pickle')
        file = os.path.abspath(basename[0] + '-graid2.xml')
        f = codecs.open(file,'w','utf-8')

        id_counter = 0

        # Verify the elements
        for element in annotation_tree.elements():

            # Get the utterance
            utterance = element[1]

            for graid2_el in utterance:
                st = graid2_el[2].get('annotation')

                if (st == ''):
                    id_counter+=1
                    continue

                # Creating the node with link
                node = doc.createElement("node")
                node.setAttribute("xml:id", "graid2-n"
                + str(id_counter)) # Node number

                # Creating the node
                link = doc.createElement("link")
                link.setAttribute("targets", "clause-r"
                + str(id_counter)) # ref
                node.appendChild(link)

                graph.appendChild(node)

                # Creating the features and the linkage
                a = doc.createElement("a")
                a.setAttribute("xml:id", "graid2-"
                + str(id_counter)) # id
                a.setAttribute("label", "graid2") # label
                a.setAttribute("ref", "graid2-n"
                + str(id_counter)) # ref
                a.setAttribute("as", "graid2") # as

                # Feature structure
                feature_st = doc.createElement("fs")
                feature = doc.createElement("f")
                feature.setAttribute("name","graid2")
                feature.setAttribute("value",st)
                value = doc.createTextNode(st) # Value
                feature.appendChild(value)
                feature_st.appendChild(feature)

                a.appendChild(feature_st)
                graph.appendChild(a)

                id_counter+=1

        # Write the content in XML file
        f.write(doc.toprettyxml(indent="  "))

        #Close XML file
        f.close()