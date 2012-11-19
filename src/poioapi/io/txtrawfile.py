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
each one of the types of data hierarchies.
"""

from xml.dom.minidom import Document

import codecs
import os

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

    def __init__(self, basedirname, annotation_tree, data_hierarchy):
        """Class's constructor.

        Parameters
        ----------
        filepath : str
            Path of the file to manipulate.

        """

        self.basedirname = basedirname
        self.annotation_tree = annotation_tree
        self.data_hierarchy = data_hierarchy
        self.filename = ''
        self.txt_file = ''
        self.loc = ''
        self.fid = ''

    def create_raw_file(self):
        """Creates an txt file with the data in the
        Annotation Tree file. Passing only the sentences.

        See Also
        --------
        create_raw_xml : Function the converts the data
        to an xml only with the regions.

        """

        file = self.basedirname + '.txt'
        f = codecs.open(file,'w', 'utf-8') # Need the encode

        self.txt_file = os.path.basename(self.basedirname + '.txt')
        self.filename = self.txt_file.split('.')
        self.filename = self.filename[0]

        # Verify the elements
        for element in self.annotation_tree.elements():

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

        # Getting the label in data hierarchy
        utt = self.data_hierarchy[0]

        doc = Document()
        graph = doc.createElement("graph")
        graph.setAttribute("xmlns", "http://www.xces.org/ns/GrAF/1.0/")
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
        file = self.basedirname + '-' + utt + '.xml'
        f = codecs.open(file,'w','utf-8')

        self.loc = os.path.basename(file)
        self.fid = utt

        # Verify the elements
        for element in self.annotation_tree.elements():

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

            # Creating the node with link
            node = doc.createElement("node")
            node.setAttribute("xml:id", utt + "-n"
            + str(seg_count)) # Node number

            # Creating the link node
            link = doc.createElement("link")
            link.setAttribute("targets", utt + "-r"
            + str(seg_count)) # ref
            node.appendChild(link)

            graph.appendChild(node)

            seg_count+=1

        # Write the content in XML file
        f.write(doc.toprettyxml(indent="  "))

        #Close XML file
        f.close()
