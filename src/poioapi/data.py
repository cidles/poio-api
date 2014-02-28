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

# Set the type of string
if sys.version_info[:2] >= (3, 0):
    string_type = str
else:
    string_type = basestring

# File types
(EAF, EAFFROMTOOLBOX, KURA, TOOLBOX, TOOLBOXXML, SHOEBOX, TREEPICKLE,
    TYPECRAFT, OBT) = range(9)

# Tier types
(TIER_UTTERANCE, TIER_WORD, TIER_MORPHEME, TIER_POS, TIER_GLOSS, TIER_GRAID1,
    TIER_GRAID2, TIER_TRANSLATION, TIER_COMMENT) = range(9)

# Tier labels
# TODO: this could be the link to the ISOcat later, where we also get the labels
tier_labels = {
    TIER_UTTERANCE: "utterance",
    TIER_WORD: "word",
    TIER_MORPHEME: "morpheme",
    TIER_POS: "part of speech",
    TIER_GLOSS: "gloss",
    TIER_GRAID1: "graid1",
    TIER_GRAID2: "graid2",
    TIER_TRANSLATION: "translation",
    TIER_COMMENT: "comment"
}

# Data structure types
(DST_WORDS, DST_GRAID, DST_GRAIDDIANA, DST_MORPHSYNT) = range(4)

class UnknownFileFormatError(Exception): pass
class NoFileSpecifiedError(Exception): pass
class UnknownDataStructureTypeError(Exception): pass
class DataStructureTypeNotSupportedError(Exception): pass
class DataStructureTypeNotCompatible(Exception): pass
class UnknownAnnotationTypeError(Exception): pass


def data_structure_handler_for_type(data_structure_type):
    if data_structure_type == DST_GRAID:
        return DataStructureTypeGraid()
    elif data_structure_type == DST_GRAIDDIANA:
        return DataStructureTypeGraidDiana()

    else:
        raise(DataStructureTypeNotSupportedError(
            "Data structure type {0} not supported".format(
            data_structure_type)))


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

    data_hierarchy = [ 'utterance', ['word'], 'translation']

    def __init__(self, custom_data_hierarchy = None):
        """Class's constructor.....

        """
        if custom_data_hierarchy != None:
            self.data_hierarchy = custom_data_hierarchy

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

    # def get_siblings_of_type(self, ann_type):
    #     """Return all the siblings of a given type in the hierarchy
    #     including the given type itself.

    #     Parameters
    #     ----------
    #     ann_type : str
    #         Value of the field in the data structure hierarchy.

    #     Returns
    #     -------
    #     ann_type : str
    #         Value of the field in the data structure hierarchy if
    #         exist.

    #     Raises
    #     ------
    #     UnknownAnnotationTypeError
    #         If the ann_type doesn't exist.

    #     """

    #     if ann_type not in self.flat_data_hierarchy:
    #         raise UnknownAnnotationTypeError

    #     if ann_type in self.data_hierarchy:
    #         return [s for s in self.data_hierarchy
    #             if isinstance(s, string_type)]

    #     for e in self.data_hierarchy:
    #         if type(e) is list:
    #             if ann_type in e:
    #                 return [s for s in e if isinstance(s, string_type)]

    #     return []

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

        # is ann_type a root type?
        if ann_type in self.data_hierarchy:
            return []

        return self._get_parents_of_type_helper(
            ann_type, self.data_hierarchy)[1]

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

    def get_children_of_type(self, ann_type):
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

        return self._get_children_of_type_helper(ann_type, self.data_hierarchy)

    def _get_children_of_type_helper(self, ann_type, hierarchy):
        """Helper function for get_children_of_type.

        Parameters
        ----------
        ann_type : str
            Value of the field in the data structure hierarchy.
        hierarchy: array_like
            An array that contains the data structure hierarchy.

        Returns
        -------
        children : array_like
            A list with the children.

        """
        for i, e in enumerate(hierarchy):
            if type(e) is list:
                return self._get_children_of_type_helper(ann_type, e)
            else:
                if e == ann_type:
                    children = []
                    if i + 1 < len(hierarchy):
                        lists = [l for l in hierarchy if type(l) is list]
                        children = [e for l in lists for e in l
                            if isinstance(e, string_type)]
                    if ann_type == self.data_hierarchy[0]:
                        children += [e for e in self.data_hierarchy[1:]
                            if isinstance(e, string_type)]
                    return children

        return []

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

    data_hierarchy = \
    [ 'utterance',
        [ 'clause_unit',
            [ 'word', 'wfw', 'graid1' ],
          'graid2' ],
      'translation', 'comment' ]

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

    data_hierarchy =\
    [ TIER_UTTERANCE,
        [ TIER_WORD,
            [ TIER_MORPHEME, [ TIER_GLOSS ] ],
            TIER_POS ],
        TIER_TRANSLATION, TIER_COMMENT ]
