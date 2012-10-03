# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
""" This module is to create the regions
of the Translation.

Note: The comments are exactly the sames for
each on of the types of data hierarchies.
"""

from xml.dom.minidom import Document
from poioapi import annotationtree
from poioapi import data

import os
import pickle
import codecs
import header

class CreateTransFile:
    """
    Class responsible to retrieve the translations of each
    sentence from the Annotation Tree.

    """

    def __init__(self, filepath):
        """Class's constructor.

        Parameters
        ----------
        filepath : str
            Path of the file to manipulate.

        """

        self.filepath = filepath
        self.loc = ''
        self.fid = ''

    def create_trans_xml(self):
        """Creates an xml file with all the translations of the
        Annotation Tree file.

        See Also
        --------
        poioapi.data : Here you can find more about the data
        hierarchies.

        """

        # Initialize the variable
        annotation_tree = annotationtree.AnnotationTree(data.GRAID)

        # Getting the label in data hierarchy
        trs = data.DataStructureTypeGraid.data_hierarchy[2]
        utt = data.DataStructureTypeGraid.data_hierarchy[0]

        # Open the file
        file = open(self.filepath, "rb")
        annotation_tree.tree = pickle.load(file)

        doc = Document()
        graph = doc.createElement("graph")
        graph.setAttribute("xmlns", "http://www.xces.org/ns/GrAF/1.0/")
        doc.appendChild(graph)

        # Header
        graphheader = doc.createElement("graphHeader")
        labelsdecl = doc.createElement("labelsDecl")
        graphheader.appendChild(labelsdecl)
        graph.appendChild(graphheader)

        dependencies = doc.createElement('dependencies')
        dependson = doc.createElement('dependsOn')
        dependson.setAttribute('f.id',utt)
        dependencies.appendChild(dependson)
        graphheader.appendChild(dependencies)

        ann_spaces = doc.createElement('annotationSpaces')
        ann_space = doc.createElement('annotationSpace')
        ann_space.setAttribute('as.id',trs)
        ann_spaces.appendChild(ann_space)
        graphheader.appendChild(ann_spaces)

        # Start XML file
        basename = self.filepath.split('.pickle')
        file = os.path.abspath(basename[0] + '-' + trs + '.xml')
        f = codecs.open(file,'w','utf-8')

        self.loc = os.path.basename(file)
        self.fid = trs

        id_counter = 0

        # Verify the elements
        for element in annotation_tree.elements():

            # Get the utterance
            utterance = element[2]

            st = utterance.get('annotation')

            if (st == ''):
                id_counter+=1
                continue

            # Creating the node with link
            node = doc.createElement("node")
            node.setAttribute("xml:id", trs + "-n"
            + str(id_counter)) # Node number

            # Creating the node
            link = doc.createElement("link")
            link.setAttribute("targets", utt + "-r"
            + str(id_counter)) # ref
            node.appendChild(link)

            graph.appendChild(node)

            # Creating the features and the linkage
            # a stands for annotation
            a = doc.createElement("a")
            a.setAttribute("xml:id", trs + "-n" +
            str(id_counter)) # id
            a.setAttribute("label", trs) # label
            a.setAttribute("ref", trs + "-n"
            + str(id_counter)) # ref
            a.setAttribute("as", trs) # as

            # Feature structure
            feature_st = doc.createElement("fs")
            feature = doc.createElement("f")
            feature.setAttribute("name",trs)
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