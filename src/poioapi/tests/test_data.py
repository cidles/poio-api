# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
"""This module contains the tests to the class
DataStrutctureType in data.py module.

This test serves to ensure the viability of the methods of
the class DataStructureType in data.py.
"""

from poioapi import data

# Initialize the DataStructureType class
data_class = data.DataStructureType()

class TestDataStructureType:
    """
    This class contain the test methods to the
    class data.py.

    """

    def test_get_siblings_of_type(self):
        """Raise an assertion if there's no siblings to return.

        Return all the siblings of a given type in the hierarchy
        including the given type itself.

        Raises
        ------
        AssertionError
            If the results there aren't the expected.

        """

        # If the ann_type value equal like this
        ann_type = 'utterance'

        # The result expected should be
        expected_result = ['utterance','translation']

        assert(data_class.get_siblings_of_type(ann_type) == expected_result)

    def test_get_parents_of_type(self):
        """Raise an assertion if there's no parents to return.

        Returns all the elements that are above a given type in the type
        hierarchy.

        Raises
        ------
        AssertionError
            If the results there aren't the expected.

        """

        # If the ann_type value equal like this
        ann_type = 'utterance'

        # The result expected should be
        expected_result = ['utterance', 'translation']

        assert(data_class.get_parents_of_type(ann_type) == expected_result)

    def test__get_parents_of_type_helper(self):
        """Raise an assertion if there's no elements to return.

        Helper function for get_parents_of_type.

        Raises
        ------
        AssertionError
            If the results there aren't the expected.

        """

        # If the ann_type and hierarchy values equal like this
        ann_type = 'clause unit'
        hierarchy =\
                  [ 'utterance',
                   [ 'clause unit',
                       [ 'word', 'wfw', 'graid1' ],
                   'graid2' ],
                   'translation', 'comment' ]

        # The result expected should be a {tuple}
        expected_result = (True, ['utterance', 'translation', 'comment'])

        assert(data_class._get_parents_of_type_helper(ann_type, hierarchy) == expected_result)

    def test_empty_element(self):
        """Raise an assertion if there's no elements to return.

        Return the appended list of a certain data hierarchy.

        Raises
        ------
        AssertionError
            If the results there aren't the expected.

        """

        # The expected result to the define data hierarchy
        expected_result = [{'id': None, 'annotation': ''},
                            [[{'id': None, 'annotation': ''}]],
                              {'id': None, 'annotation': ''}]

        assert(data_class.empty_element() == expected_result)

    def test__append_list(self):
        """Raise an assertion if the elements list is invalid.

        Append element values and it's ids to the data structure elements.

        Raises
        ------
        AssertionError
            If the results there aren't the expected.

        """

        # If the element value equal like this
        element = ['word', 'wfw', 'graid1']

        # The result expected should be
        expected_result = [{'id': None, 'annotation': ''},
                {'id': None, 'annotation': ''},
                {'id': None, 'annotation': ''}]

        assert(data_class._append_list(element) == expected_result)

    def test_test_flatten_hierarchy_elements(self):
        """Raise an assertion if the elements aren't correct.

        Flat the elements appended to a new list of elements.

        Raises
        ------
        AssertionError
            If the results there aren't the expected.

        """

        # If the elements value equal like this
        elements =\
           [ 'utterance',
               [ 'clause unit',
                   [ 'word', 'wfw', 'graid1' ],
                 'graid2' ],
             'translation', 'comment' ]

        # The result expected should be
        expected_result = ['utterance',
                           'clause unit',
                           'word', 'wfw', 'graid1',
                           'graid2',
                           'translation',
                           'comment']

        assert(data_class._flatten_hierarchy_elements(elements) == expected_result)