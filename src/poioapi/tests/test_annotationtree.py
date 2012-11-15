# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
"""This module contains the tests to the class
AnnotationTree and AnnotationTreeFilter in
annotationtree.py module.

This test serves to ensure the viability of the
methods of the class AnnotationTree and
AnnotationTreeFilter in annotationtree.py.

Note: The tests made on this use Data Structure
Graid.
"""

from poioapi import data
from poioapi import annotationtree

import pickle

# Initialize the DataStructureType class
data_class = data.DataStructureTypeGraid()

# Initialize the AnnotationTree class
annotationtree_class = annotationtree.AnnotationTree(data_class)

# Initialize the AnnotationTreeFilter class
anntreefilter_class = annotationtree.AnnotationTreeFilter(data_class)

# Open the file and set it to the AnnotationTree
filepath = 'Example.pickle'
file = open(filepath, "rb")
annotationtree_class.tree = pickle.load(file)

class TestAnnotationTree:
    """
    This class contain the test methods to the
    class annotation.py.

    """

    def test_next_annotation_id(self):
        """Raise an assertion if the next id isn't correct.

        Returns the next annotation id.

        Raises
        ------
        AssertionError
            If the results there aren't the expected.

        """

        # If the class variable value equal like this
        annotationtree_class._next_annotation_id = 1

        # The result expected should be
        expected_result = 2

        assert(annotationtree_class._next_annotation_id == expected_result)

    def test_next_annotation_id(self):
        """Raise an assertion if the id type isn't int.

        Set the id of the next_annotation_id.

        Raises
        ------
        AssertionError
            If the next_id is not a int value type.

        """

        # The result expected should be
        expected_result = annotationtree_class._next_annotation_id

        assert(annotationtree_class._next_annotation_id == expected_result)

    def test_elements(self):
        """Raise an assertion if can't retrieve any element.

        Retrieve the elements of the tree.

        Raises
        ------
        AssertionError
            If the results there aren't the expected.

        """

        # Auxiliary variable
        aux_element = 'utterance'

        # Append the element to see the results
        annotationtree_class.append_element(aux_element,False)

        for element in annotationtree_class.elements():
            # The result expected should be
            expected_result = element

        assert(aux_element == expected_result)

    def test_remove_element(self):
        """Raise an assertion if can't remove an element.

        Remove an element with a certain id.

        Raises
        ------
        AssertionError
            If the results there aren't the expected.

        """

        # If the variables value equal like this
        id_element = 0

        # The result expected should be
        expected_result = False

        assert(annotationtree_class.remove_element(id_element) == expected_result)

    def test_insert_element(self):
        """Raise an assertion if can't insert an element.

        Insert an element with a certain id.

        Raises
        ------
        AssertionError
            If the results there aren't the expected.

        """

        # If the variables value equal like this
        element = [{'id': 1, 'annotation': ''},
            [[{'id': 2, 'annotation': ''},
                [[{'id': 3, 'annotation': ''},
                        {'id': 4, 'annotation': ''},
                        {'id': 5, 'annotation': ''}]],
                    {'id': 6, 'annotation': ''}]],
                {'id': 7, 'annotation': ''},
                {'id': 8, 'annotation': ''}]
        id_element = 20
        after = False
        update_ids = False

        # The result expected should be
        expected_result = True

        assert(annotationtree_class.insert_element(element, id_element, after, update_ids) == expected_result)

    def __len__(self):
        """Raise an assertion if doesn't exist any tree.

        Return the size of the tree, number of elements.

        Raises
        ------
        AssertionError
            If the results there aren't the expected.

        """

        assert(annotationtree_class.__len__() > 0)

    def test_last_filter(self):
        """Raise an assertion if can't return the
        last filter.

        Return the latest added filter.

        Raises
        ------
        AssertionError
            If the results there aren't the expected.

        """

        # The result expected should be
        expected_result = anntreefilter_class.data_structure_type

        # Comparing the result of the two instances
        assert(annotationtree_class.last_filter().data_structure_type == expected_result)

    def test_pop_filter(self):
        """Raise an assertion if can't remove filter.

        Remove and return item at index.

        Raises
        ------
        AssertionError
            If the results there aren't the expected.

        """

        # Depending on the value of the filters

        # Set some values to filters
        #annotationtree_class.filters.append('text')

        # The result expected should be
        expected_result = None

        assert(annotationtree_class.pop_filter() ==
               expected_result)

    def test__element_as_table(self):
        """Raise an assertion if can't insert an element into
        a table.

        Insert an element into a table.

        Raises
        ------
        AssertionError
            If the results there aren't the expected.

        """

        # Force the Structure Type
        annotationtree_class.structure_type_handler = data.DataStructureTypeGraid()

        # Open the file and set it to the AnnotationTree
        filepath = 'Example.pickle'
        file = open(filepath, "rb")
        annotationtree_class.tree = pickle.load(file)

        # If the variables value equal like this
        elements = [{'id': 6, 'annotation': 'gu\u0161-\u012bt:'},
            [[{'id': 4, 'annotation': 'gu\u0161-\u012bt:'},
                [[{'id': 1, 'annotation': 'gu\u0161-\u012bt:'},
                        {'id': 2, 'annotation': 'say.PRS-3SG'},
                        {'id': 3, 'annotation': ''}]],
                    {'id': 5, 'annotation': 'nc'}]],
                {'id': 7, 'annotation': 'They say:'},
                {'id': 8, 'annotation': ''}]

        data_hierarchy =\
        [ 'utterance',
            [ 'clause unit',
                [ 'word', 'wfw', 'graid1' ],
              'graid2' ],
          'translation', 'comment' ]

        table = [{0: ('gu\u0161-\u012bt:', 1)},
                {0: ('gu\u0161-\u012bt:', 1)},
                {0: ('gu\u0161-\u012bt:', 1)},
                {0: ('say.PRS-3SG', 1)},
                {0: ('&nbsp;', 1)}, {0: ('nc', 1)},
                {0: ('They say:', 1)}, {0: ('&nbsp;', 1)}]

        column = 0

        # The result expected should be
        expected_result = 0 # Return the numbers of inserted elements

        assert(annotationtree_class._element_as_table(elements, data_hierarchy, table, column) == expected_result)

class TestAnnotationTreeFilter:

    def test_element_passes_filter(self):
        """Raise an assertion if can't pass the filter.

        Verify if a specific element passes in through
        a filter.

        Raises
        ------
        AssertionError
            If the results there aren't the expected.

        """

        # Open the file and set it to the AnnotationTree
        filepath = 'Example.pickle'
        file = open(filepath, "rb")
        annotationtree_class.tree = pickle.load(file)

        # If the variables value equal like this
        element = [{'id': 6, 'annotation': 'gu\u0161-\u012bt:'},
            [[{'id': 4, 'annotation': 'gu\u0161-\u012bt:'},
                [[{'id': 1, 'annotation': 'gu\u0161-\u012bt:'},
                        {'id': 2, 'annotation': 'say.PRS-3SG'},
                        {'id': 3, 'annotation': ''}]],
                    {'id': 5, 'annotation': 'nc'}]],
                {'id': 7, 'annotation': 'They say:'},
                {'id': 8, 'annotation': ''}]

        # The result expected should be
        expected_result = True # Boolean value

        assert(anntreefilter_class.element_passes_filter(element)
               == expected_result)

    def test_passes_filter(self):
        """Raise an assertion if can't pass the filter.

        Verify if a specific element passes in through
        a filter.

        Raises
        ------
        AssertionError
            If the results there aren't the expected.

        """

        # Open the file and set it to the AnnotationTree
        filepath = 'Example.pickle'
        file = open(filepath, "rb")
        annotationtree_class.tree = pickle.load(file)

        # If the variables value equal like this
        elements = [{'id': 6, 'annotation': 'gu\u0161-\u012bt:'},
            [[{'id': 4, 'annotation': 'gu\u0161-\u012bt:'},
                [[{'id': 1, 'annotation': 'gu\u0161-\u012bt:'},
                        {'id': 2, 'annotation': 'say.PRS-3SG'},
                        {'id': 3, 'annotation': ''}]],
                    {'id': 5, 'annotation': 'nc'}]],
                {'id': 7, 'annotation': 'They say:'},
                {'id': 8, 'annotation': ''}]

        passed = True
        hirerarchy = data_class.data_hierarchy

        # The result expected should be
        expected_result = True # Boolean value

        assert(anntreefilter_class._passes_filter(passed, elements, hirerarchy)
               == expected_result)
