# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: Peter Bouda <pbouda@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

from __future__ import unicode_literals

import os.path
import codecs

from poioapi import data
from graf import GraphParser

class AnnotationGraph():

    def __init__(self, data_structure_type):
        self.data_structure_type = data_structure_type

        if data_structure_type == data.GRAID:
            self.structure_type_handler = data.DataStructureTypeGraid()
        elif data_structure_type == data.GRAIDDIANA:
            self.structure_type_handler = data.DataStructureTypeGraidDiana()
        elif data_structure_type == data.MORPHSYNT:
            self.structure_type_handler = data.DataStructureTypeMorphsynt()
        else:
            self.structure_type_handler = None

        self.graf = None
        self.graf_basename = None


    def load_graph_from_graf(self, filepath):
        """Load the project annotation graph from a GrAF/XML file.

        Parameters
        ----------
        filepath : str
            The absolute path to a file.

        """
        parser = GraphParser()
        self.graf = parser.parse(filepath)
        (self.graf_basename, _) = os.path.splitext(os.path.abspath(filepath))

    def elements(self):
        """Retrieve the elements from the annotation graph. Elements are
        sub-graph that have the root node of the data structure type as
        the root node.

        Returns
        -------
        elements : list
            Return elements of the graph.

        """
        # read the base data to get string for regions
        base_data_file = self.graf_basename + ".txt"
        f = codecs.open(base_data_file, "r", "utf-8")
        base_data = f.read()
        f.close()

        base_tier_name =  self.structure_type_handler.flat_data_hierarchy[0]
        for (node_id, node) in self.graf.nodes.items():
            if node_id.startswith(base_tier_name):
                region = node.links[0][0]
                utterance = base_data[region.start:region.end]
        return []

    def get_all_neighbours_for_node(self, node_id, neighbour_type):
        """Retreive all neighbour annotations for a given nodes. The parameter
        neighbour_type specifies the type if the neigbours. For example if
        the node is an utterance the neighbour type "word" specifies that
        all "word" annotations that are connected to the utterance should
        be returned. The neighbour type must be a parent or child if the node's
        type in the data hierarchy.

        Parameters
        ----------
        node_id : str
            The ID of the node to start the search.
        neighbour_type : str
            The type of the neighbours to search.

        Returns
        -------
        neighbours : list of node ids

        """

        return []