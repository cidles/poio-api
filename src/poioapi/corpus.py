# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: Peter Bouda <pbouda@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT
"""
The corpus module contains classes to handle collections of work items
(currently: annotation trees; later: annotation graphs). It connects those
work items to files on disk to keep track of the corpus the user works with.
Each class provides a simple list of items to go through all work items for
queries and updates. The queries and updates are handle by the classes of the
work items.
"""

from __future__ import unicode_literals

import poioapi.data
import poioapi.annotationtree
import poioapi.annotationgraph

class CorpusTrees():

    def __init__(self, data_structure_type):
        self.items = []
        self.data_structure_type = data_structure_type

    def add_item(self, filepath, filetype):
        if filetype == poioapi.data.TREEPICKLE:
            annotation_tree = poioapi.annotationtree.AnnotationTree(
                poioapi.data.data_structure_handler_for_type(
                    self.data_structure_type
                )
            )
            annotation_tree.load_tree_from_pickle(filepath)
            if annotation_tree.structure_type_handler != self.data_structure_type:
                raise(
                    poioapi.data.DataStructureTypeNotCompatible(
                        "Data structure type {0} not compatible with corpus"
                        "data type {1}".format(
                            annotation_tree.structure_type_handler,
                            self.data_structure_type)))

            annotation_tree.init_filters()
            self.items.append( (filepath, annotation_tree) )
        else:
            raise poioapi.data.UnknownFileFormatError()


class CorpusGraphs():

    def __init__(self):
        self.items = []
        #self.data_structure_type = None
        self.tier_names = set()

    def add_item(self, filepath, filetype):
        annotation_graph = poioapi.annotationgraph.AnnotationGraph(None)
        if filetype == poioapi.data.EAF:
            annotation_graph.from_elan(filepath)
        elif filetype == poioapi.data.TYPECRAFT:
            annotation_graph.from_typecraft(filepath)
        else:
            raise poioapi.data.UnknownFileFormatError()

        annotation_graph.structure_type_handler = \
            poioapi.data.DataStructureType(
                annotation_graph.tier_hierarchies[0]
            )

        self.tier_names.update(annotation_graph.structure_type_handler.flat_data_hierarchy)

        #annotation_tree.init_filters()
        self.items.append( (filepath, annotation_graph) )
