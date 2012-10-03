# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
""" This document is to create the regions
of the words in the clause units one by one.
"""

from xml.dom.minidom import Document
from poioapi import annotationtree
from poioapi import data

import os
import pickle
import codecs

class CreateClauseUnitsFile:
    """
    Class responsible to retrieve the clause units
    from the Annotation Tree.

    The data hierarchy set in the Annotation Tree
    must be the GRAID hierarchy.

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

    def create_clause_units_file(self):
        """Creates an xml file with all the clause units of the
        Annotation Tree file.

        See Also
        --------
        poioapi.data : Here you can find more about the data
        hierarchies.

        """

        # Initialize the variable
        annotation_tree = annotationtree.AnnotationTree(data.GRAID)

        # Getting the label in data hierarchy
        word = data.DataStructureTypeGraid.data_hierarchy[1]
        clause_aux = word[0].replace(' ', '_')

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

        # Auxiliary variables
        seg_count = 0
        last_counter = 0

        # Start XML file
        basename = self.filepath.split('.pickle')
        file = os.path.abspath(basename[0] + '-' + clause_aux + '.xml')
        f = codecs.open(file,'w','utf-8')

        self.loc = os.path.basename(file)
        self.fid = clause_aux

        # Verify the elements
        for element in annotation_tree.elements():

            # Get the clause unit
            clause_units = element[1]

            for clause in clause_units:
                st = clause[0].get('annotation')
                region = doc.createElement("region")
                region.setAttribute("xml:id",
                    clause_aux + "-r" + str(seg_count)) # Region
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