# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT
"""This module contains a simple example 
how to use the PoioAPI and search
some of the elements in an AnnotationTree.
"""

import copy
import pickle

from poioapi import corpus
from poioapi import annotationtree
from poioapi import data

# Initialize the variable
annotation_tree = annotationtree.AnnotationTree(data.GLOSS)

# Open the file and set it to the AnnotationTree
filepath = 'Balochi Text1.pickle'
file = open(filepath, "rb")
annotation_tree.tree = pickle.load(file)

# Initialize the list that will contain the result values
filterChain = []

# Choose the data structure type
data_structure_type = data.DataStructureTypeGraid()

# Initialize the corpus to the file reader
corpus = corpus.CorpusTrees(data_structure_type)
corpus.add_item(filepath, data.TREEPICKLE)

# Set the filter structure
currentFilter = annotationtree.AnnotationTreeFilter(data_structure_type)

# Most important part set the filter with the defined words to search in each part of the data structure
# for ann_type in data_structure_type.flat_data_hierarchy:
#     # Find a way to set the text here
#     currentFilter.set_filter_for_type(ann_type, unicode(value))
# But for let's use a directly approach

# This two variables representes a field of structure and it's value
ann_type = 'uterance' # utterance, word, wfw, ...
filter_string = ''# any value

# Setting the values to the filter
currentFilter.set_filter_for_type(ann_type, filter_string)

currentFilter.set_inverted_filter(True) # Inverted filter use a boolean value
currentFilter.set_contained_matches(False) # Inverted filter use a boolean value

# Only can use one of the two operations
AndOperation = True # And Operation use a boolean value
OrOperation = False # Or Operation use a boolean value

if AndOperation:
    currentFilter.set_boolean_operation(annotationtree.AnnotationTreeFilter.AND)
elif OrOperation:
    currentFilter.set_boolean_operation(annotationtree.AnnotationTreeFilter.OR)

filterChain.append(currentFilter)

for _, annotationtree in corpus.items:
    annotationtree.init_filters()
    for filter in filterChain:
        annotationtree.append_filter(copy.deepcopy(filter))

# Verify the elements
for element in annotation_tree.elements():
    print(element)
    print("\n")
