# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: Peter Bouda <pbouda@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT
"""This module contains the classes to access annotated data in
various formats.

The parsing is done by Builder classes for each file type, i.e.
Elan's .eaf files, Kura's .xml file, Toolbox's .txt files etc.
"""

from __future__ import unicode_literals

import sys
import re as regex

# Set the type of string
if sys.version_info[:2] >= (3, 0):
    string_type = str
else:
    string_type = basestring

# File types
(EAF, EAFFROMTOOLBOX, KURA, TOOLBOX, TREEPICKLE) = range(5)

# Data structure types
(GLOSS, WORDS, GRAID, GRAIDDIANA) = range(4)

class UnknownFileFormatError(Exception): pass
class NoFileSpecifiedError(Exception): pass

# Data structure types
(WORDS, MORPHSYNT, GRAID) = range(3)
class UnknownDataStructureTypeError(Exception): pass
class DataStructureTypeNotSupportedError(Exception): pass
class DataStructureTypeNotCompatible(Exception): pass
class UnknownAnnotationTypeError(Exception): pass

class DataStructureType(object):
    """
    Data structure type constructor.
        
    Attributes
    ----------
    `name` : str
        Name of the structure.
    data_hirerarchy : array
        Structure of the array.

    """

    name = "WORDS"

    data_hierarchy = [ 'utterance', ['word'], 'translation']
    types_with_regions = [ 'utterance', 'clause_unit', 'word' ]

    def __init__(self):
        """Class's constructor.....

        """

        self.flat_data_hierarchy = self._flatten_hierarchy_elements(
            self.data_hierarchy)
        self.nr_of_types = len(self.flat_data_hierarchy)

    def type_has_region(self, ann_type):
        """ Checks whether the given type has regions that connect it
        to the base data.

        Parameters
        ----------
        ann_type : str
            Value of the field in the data structure hierarchy.

        Returns
        -------
        is_region : bool
            Whether the annotation type has regions.
        """
        return (ann_type in self.types_with_regions)

    def get_siblings_of_type(self, ann_type):
        """Return all the siblings of a given type in the hierarchy
        including the given type itself.

        Parameters
        ----------
        ann_type : str
            Value of the field in the data structure hierarchy.

        Returns
        -------
        ann_type : str
            Value of the field in the data structure hierarchy if
            exist.

        Raises
        ------
        UnknownAnnotationTypeError
            If the ann_type doesn't exist.

        """

        if ann_type not in self.flat_data_hierarchy:
            raise UnknownAnnotationTypeError

        if ann_type in self.data_hierarchy:
            return [s for s in self.data_hierarchy if isinstance(s, string_type)]

        for e in self.data_hierarchy:
            if type(e) is list:
                if ann_type in e:
                    return [s for s in e if isinstance(s, string_type)]

    def get_parents_of_type(self, ann_type):
        """Returns all the elements that are above a given type in the type
        hierarchy.

        Parameters
        ----------
        ann_type : str
            Value of the field in the data structure hierarchy.

        Returns
        -------
        _get_parents_of_type_helper : array_like
            The return result depends on the return of the called method.

        See Also
        --------
        _get_parents_of_type_helper

        """

        if ann_type not in self.flat_data_hierarchy:
            raise UnknownAnnotationTypeError

        return self._get_parents_of_type_helper(ann_type, self.data_hierarchy)[1]

    def _get_parents_of_type_helper(self, ann_type, hierarchy):
        """Helper function for get_parents_of_type.

        Parameters
        ----------
        ann_type : str
            Value of the field in the data structure hierarchy.
        hierarchy: array_like
            An array that contains the data structure hierarchy.

        Returns
        -------
        found : array_like
            The actual list with the appended elements.
        parents : array_like
            The actual list with the appended elements.

        """

        parents = []
        found = False
        for e in hierarchy:
            if type(e) is list and not found:
                if ann_type in e:
                    found = True
                else:
                    found, add_parents = self._get_parents_of_type_helper(
                        ann_type, e)
                    if found:
                        parents += add_parents
            else:
                parents.append(e)
        return found, parents

    def empty_element(self):
        """Return the appended list of a certain data hierarchy.

        Returns
        -------
        _append_list : array_like
            The actual list with the appended elements.

        """

        return self._append_list(self.data_hierarchy)

    def _append_list(self, element):
        """Append element values and it's ids to the data structure elements.

        Parameters
        ----------
        element : str

        Returns
        -------
        ret : array_like
            A list with appended `element`values.

        """

        ret = []
        for e in element:
            if type(e) is list:
                l = self._append_list(e)
                ret.append([l])
            else:
                ret.append({ 'id': None, 'annotation': '' })
        return ret

    def _flatten_hierarchy_elements(self, elements):
        """Flat the elements appended to a new list of elements.

        Parameters
        ----------
        elements : array_like
            An array of string values.

        Returns
        -------
        flat_elements : array_like
            An array of faltten `elements`.

        """

        flat_elements = []
        for e in elements:
            if type(e) is list:
                flat_elements.extend(self._flatten_hierarchy_elements(e))
            else:
                flat_elements.append(e)
        return flat_elements

class DataStructureTypeGraid(DataStructureType):

    """
    Data structure type using a GRAID format.

    Attributes
    ----------
    `name` : str
        Name of the structure.
    data_hirerarchy : array_like
        Structure of the array.

    """

    name = "GRAID"

    data_hierarchy = \
    [ 'utterance',
        [ 'clause_unit',
            [ 'word', 'wfw', 'graid1' ],
          'graid2' ],
      'translation', 'comment' ]

    types_with_regions = \
    [ 'utterance', 'clause_unit', 'word' ]

class DataStructureTypeGraidDiana(DataStructureType):

    """
    Data structure type using a GRAID format.

    Attributes
    ----------
    `name` : str
        Name of the structure.
    data_hirerarchy : array_like
        Structure of the array.

    """

    name = "GRAIDDIANA"

    data_hierarchy =\
    [ 'utterance',
        [ 'clause_unit',
            [ 'word',
                [ 'morpheme',
                  'gloss'
                ],
              'graid1',
              'graid3'
            ],
          'graid2'
      ],
      'translation',
      'ref',
      'comment'
    ]

    types_with_regions =\
    [ 'utterance', 'clause_unit', 'word', 'morpheme' ]


class DataStructureTypeMorphsynt(DataStructureType):

    """
    Data structure type using a Morphsyntax format.

    Attributes
    ----------
    `name` : str
        Name of the structure.
    data_hirerarchy : array_like
        Structure of the array.

    """

    name = "MORPHSYNT"

    data_hierarchy =\
    [ 'utterance',
        [ 'word',
            [ 'morpheme',
                [ 'gloss'] ] ],
        'translation', 'comment' ]

    types_with_regions =\
    [ 'utterance', 'word', 'morpheme' ]