# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
""" This module is to create the regions
of the gloss one by one in a Morphsyntax
data hierarchy.
"""

from xml.dom.minidom import Document
from poioapi import annotationtree
from poioapi import data

import os
import pickle
import codecs

class CreateMorphGlossFile:
    """
    Class responsible to retrieve the gloss words
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
        self.loc = ''
        self.fid = ''

    def create_gloss_xml(self):
        """Creates an xml file with all the gloss words of the
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
        word = word[1]
        morph = word[0]
        gloss = word[1]
        gloss = gloss[0]

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
        dependson.setAttribute('f.id',morph)
        dependencies.appendChild(dependson)
        graphheader.appendChild(dependencies)

        ann_spaces = doc.createElement('annotationSpaces')
        ann_space = doc.createElement('annotationSpace')
        ann_space.setAttribute('as.id',gloss)
        ann_spaces.appendChild(ann_space)
        graphheader.appendChild(ann_spaces)

        # Start XML file
        basename = self.filepath.split('.pickle')
        file = os.path.abspath(basename[0] + '-' + gloss + '.xml')
        f = codecs.open(file,'w','utf-8')

        self.loc = os.path.basename(file)
        self.fid = gloss

        id_counter = 0

        # Verify the elements
        for element in annotation_tree.elements():

            # Get the utterance
            utterance = element[1]

            for gloss_el in utterance:
                for el in gloss_el[1]:

                    st = el[0].get('annotation')

                    if (st == ''):
                        id_counter+=1
                        continue

                    # Creating the node with link
                    node = doc.createElement("node")
                    node.setAttribute("xml:id", gloss + "-n"
                    + str(id_counter)) # Node number

                    # Creating the node
                    link = doc.createElement("link")
                    link.setAttribute("targets", morph + "-r"
                    + str(id_counter)) # ref
                    node.appendChild(link)

                    graph.appendChild(node)

                    # Creating the features and the linkage
                    a = doc.createElement("a")
                    a.setAttribute("xml:id", gloss + "-"
                    + str(id_counter)) # id
                    a.setAttribute("label", gloss) # label
                    a.setAttribute("ref", gloss + "-n"
                    + str(id_counter)) # ref
                    a.setAttribute("as", gloss) # as

                    # Feature structure
                    feature_st = doc.createElement("fs")
                    feature = doc.createElement("f")
                    feature.setAttribute("name",gloss)
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