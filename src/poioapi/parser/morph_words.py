# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
""" This document is to create the regions
of the words in the utterance in a Morphsyntax
data hierarchy.
"""

from xml.dom.minidom import Document
from poioapi import annotationtree
from poioapi import data

import os
import pickle
import codecs

class CreateMorphWordsFile:
    """
    Class responsible to retrieve the words
    from the Annotation Tree.

    The data hierarchy set in the Annotation Tree
    must be the MORPHSYNT (Morphsyntax) hierarchy.

    """

    def __init__(self, filepath):
        """Class's constructor.

        Parameters
        ----------
        filepath : str
            Path of the file to manipulate.

        """

        self.filepath = filepath

    def create_words_file(self):
        """Creates an xml file with all the words of the
        Annotation Tree file.

        See Also
        --------
        poioapi.data : Here you can find more about the data
        hierarchies.

        """

        # Initialize the variable
        annotation_tree = annotationtree.AnnotationTree(data.MORPHSYNT)

        # Getting the label in data hierarchy
        word = data.DataStructureTypeMorphsynt.data_hierarchy[1]
        word = word[0]

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

        # Auxiliary variables
        seg_count = 0
        last_counter = 0

        # Start XML file
        basename = self.filepath.split('.pickle')
        file = os.path.abspath(basename[0] + '-m' + word + '.xml')
        f = codecs.open(file,'w','utf-8')

        # Verify the elements
        for element in annotation_tree.elements():

            # Get the clause unit
            words = element[1]

            for word_el in words:
                st = word_el[0].get('annotation')
                region = doc.createElement("region")
                region.setAttribute("xml:id",
                    word + "-r" + str(seg_count)) # Region
                region.setAttribute("anchors",
                    str(last_counter) + " "
                    + str(last_counter + len(st))) # Anchors

                graph.appendChild(region)

                # Update the last_counter
                last_counter += len(st)

                seg_count+=1

        # Write the content in XML file
        f.write(doc.toprettyxml(indent="  "))

        #Close XML file
        f.close()