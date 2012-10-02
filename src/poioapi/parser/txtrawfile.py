# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
""" This module is to create the raw txt
file form the pickle file.

Note: The comments are exactly the sames for
each on of the types of data hierarchies.
"""

from xml.dom.minidom import Document
from poioapi import annotationtree
from poioapi import data

import codecs
import os
import pickle

class CreateRawFile:
    """
    Class responsible to create a raw file from
    the Annotation Tree.

    There are created to files. One of them is a
    txt file that is the data from the AnnotationTree
    file converted to text and the other file is
    a xml that contain the regions of each sentence in
    the txt file.
    """

    def __init__(self, filepath):
        """Class's constructor.

        Parameters
        ----------
        filepath : str
            Path of the file to manipulate.

        """

        self.filepath = filepath

    def create_raw_file(self):
        """Creates an txt file with the data in the
        Annotation Tree file. Passing only the sentences.

        See Also
        --------
        create_raw_xml : Function the converts the data
        to an xml only with the regions.

        """

        # Initialize the variable
        annotation_tree = annotationtree.AnnotationTree(data.GRAID)

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

        self.create_raw_xml()

    def create_raw_xml(self):
        """Creates an xml file with the regions of the data
        in the Annotation Tree file.

        See Also
        --------
        create_raw_file : Function the converts the data
        to an txt with the sentences from the Annotation
        Tree file.

        """

        # Initialize the variable
        annotation_tree = annotationtree.AnnotationTree(data.GRAID)

        # Getting the label in data hierarchy
        utt = data.DataStructureTypeGraid.data_hierarchy[0]

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
        file = os.path.abspath(basename[0] + '-' + utt + '.xml')
        f = codecs.open(file,'w','utf-8')

        # Verify the elements
        for element in annotation_tree.elements():

            # Get the utterance
            utterance = element[0]

            counter = last_counter

            last_counter += len(utterance.get('annotation'))

            region = doc.createElement("region")
            region.setAttribute("xml:id", utt + "-r"
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