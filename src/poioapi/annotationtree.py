# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: Peter Bouda <pbouda@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

"""This module contains the classes to access annotated data in
an annotation tree. An annotation tree is a tree-like structure,
dependant on the "data structure type". Data structure types 
are for example "morpho-syntactic", "part-of-speech", "GRAID".

Depending on the data structure type the necessary annoations 
are read from the input file. The class 
data.AnnotationFileObject and sub-classes are used
Wto read and write files.
"""

from __future__ import unicode_literals

#import regex as re
import re
import pickle
import operator

from poioapi import data
#from poioapi.io.pickle import Writer

class RegionNotFoundInString(Exception):
    """Base class for region update method exception."""

class AnnotationTree():
    """
    AnnotationTree tree-like structure 
    constructor.

    """

    def __init__(self, data_structure_type = None):
        """Class constructor.

        Parameters
        ----------
        data_structure_type : poioapi.data.DataStructureType
            The data structure type (default = None).

        """

        self.tree = []
        self._next_annotation_id = 0

        if data_structure_type != None:
            self.reset_data_structure_type(data_structure_type)

        self.filters = []
        self.filtered_element_ids = [[]]

    def reset_data_structure_type(self, data_structure_type):
        """
        Sets the data structure type to the given value. Initializes the
        class that handles the data structure type.

        Parameters
        ----------
        data_structure_type : poioapi.data.DataStructureType
            The data structure type.

        Raises
        ------
        poioapi.data.DataStructureTypeNotSupportedError
            If the given data structure type is not inherits from DataStructureType.
        """

        if data_structure_type is None:
            self.structure_type_handler = None
        elif isinstance(data_structure_type, data.DataStructureType):
            self.structure_type_handler = data_structure_type
        else:
            raise(
                data.DataStructureTypeNotSupportedError(
                    "Data structure type {0} not supported".format(
                        data_structure_type)))

    @property
    def next_annotation_id(self):
        """Returns the next annotation id.

        Returns
        -------
        next_annotation_id : int
            The return result is the increment of the previous annotation
            id.

        """

        self._next_annotation_id += 1
        return self._next_annotation_id

    @next_annotation_id.setter
    def next_annotation_id(self, next_id):
        """Increment the id of the next_annotation_id.

        Parameters
        ----------
        next_id : int
            The next id value.

        Returns
        -------
        _next_annotation_id : int
            The return result is the increment of the previous annotation
            id.

        Raises
        ------
        TypeError
            If the next_id is not a int value type.

        """

        if type(next_id) is not int:
            raise(TypeError, "annotation ID must be int")
        self._next_annotation_id = next_id

    def save_tree_as_pickle(self, filepath):
        """Save the project annotation tree in a pickle
        file.

        Parameters
        ----------
        filepath : str
            The absolute path to a file.

        """

        file = open(filepath, "wb")
        pickle.dump(self.tree, file)
        file.close()

    def load_tree_from_pickle(self, filepath):
        """Load the project annotation tree from a pickle
        file.

        Parameters
        ----------
        filepath : str
            The absolute path to a file.

        """

        file = open(filepath, 'rb')
        loaded_data = pickle.load(file)
        if loaded_data[0] == 'poio_pickle_v2':
            self.reset_data_structure_type(
                data.data_structure_handler_for_type(loaded_data[1])
            )
            self.tree = loaded_data[2]
        else:
            file.seek(0)
            self.reset_data_structure_type(data.DataStructureTypeGraid())
            self.tree = pickle.load(file)
        file.close()

    def save_tree_as_graf(self, filepath):
        """Save the project as GrAF.

        Parameters
        ----------
        filepath : str
            The absolute path to a file.

        """

        Writer(self.tree, filepath).write()

    def append_element(self, element, update_ids = False):
        """Append an element to the annotation tree.

        Parameters
        ----------
        element : str
            Value of a field in the data structure annotation tree.
        update_ids: bool
            To update or not the ids of the annotation tree.

        """

        if update_ids:
            self.tree.append(self._update_ids_of_element(element))
        else:
            self.tree.append(element)

    def _update_ids_of_element(self, element):
        """Update the ids of the element in the annotation tree.

        Parameters
        ----------
        element : str
            Value of a field in the data structure annotation tree.

        Returns
        -------
        element_with_ids : array_like
            An array filled with the updated ids of the tree.

        """

        element_with_ids = []
        for e in element:
            if type(e) is dict:
                element_with_ids.append({ 'id': self.next_annotation_id, 'annotation': e['annotation'] })
            elif type(e) is list:
                element_with_ids.append(self._update_ids_of_element(e))
        return element_with_ids

    def empty_element(self):
        """Retrieve the array with the updated ids.

        Returns
        -------
        _update_ids_of_element : array_like
            The return result depends on the return of the called method.

        See Also
        --------
        _update_ids_of_element

        """

        empty_element = self.structure_type_handler.empty_element()
        return self._update_ids_of_element(empty_element)

    def append_empty_element(self):
        """Append an element with the ids.

        See Also
        --------
        empty_element

        """

        empty_element = self.empty_element()
        self.tree.append(empty_element)

    def elements(self):
        """Retrieve the elements of the tree.

        Returns
        -------
        e : array_like
            Return elements of the tree.

        """

        return (e for e in self.tree)

    def remove_element(self, id_element):
        """Remove an element with a certain id.

        Parameters
        ----------
        id_element : int
            Id of an element.

        Returns
        -------
        remove_element : bool
            Return an answer true or false.

        """

        for i, e in enumerate(self.tree):
            if e[0]['id'] == id_element:
                self.tree.pop(i)
                return True
        return False

    def insert_element(self, element, id_element, after = False,
                       update_ids = False):
        """Insert an element with a certain id.

        Parameters
        ----------
        element : str
            Value of a field in the data structure annotation tree.
        id_element : int
            Id of an element.
        after : bool
        update_ids: bool
            To update or not the ids of the annotation tree.

        Returns
        -------
        insert_element : bool
            Return an answer true or false.

        """

        if update_ids:
            element = self._update_ids_of_element(element)
        for i, e in enumerate(self.tree):
            if e[0]['id'] == id_element:
                if after:
                    self.tree.insert(i + 1, element)
                else:
                    self.tree.insert(i, element)
                return True
        return False

    def __len__(self):
        """Return the size of the tree, number of elements.

        Returns
        -------
        len(tree) : int
            Return the size of the tree, number of elements.

        """

        return len(self.tree)

    def append_filter(self, filter):
        """Append a filter to the search.

        Parameters
        ----------
        filter : str
            Value to set the fiter.

        """

        self.filters.append(filter)
        new_filtered_elements = [i
                                 for i, e in enumerate(self.tree)
                                 if i in self.filtered_element_ids[-1] and
                                    filter.element_passes_filter(e)]
        self.filtered_element_ids.append(new_filtered_elements)

    def last_filter(self):
        """Return the latest added filter.

        Returns
        -------
        filters = array_like
            An array with the filters.
        AnnotationTreeFilter : class
            Return the class AnnotationTreeFilter.

        """

        if len(self.filters) > 0:
            return self.filters[-1]
        else:
            return AnnotationTreeFilter(self.structure_type_handler)

    def update_last_filter(self, filter):
        """Update the last filter added.

        Parameters
        ----------
        filter : str
            Value to set the fiter.

        """

        self.pop_filter()
        self.append_filter(filter)

    def pop_filter(self):
        """Remove and return item at index.

        Returns
        -------
        filters.pop = str
            Item at index.

        """

        if len(self.filters) > 0:
            self.filtered_element_ids.pop()
            return self.filters.pop()
        return None

    def init_filters(self):
        """Initialize the filters array.

        """

        self.filters = []
        self.filtered_element_ids = [ range(len(self.tree)) ]

    def reset_filters(self):
        """Reset the filters array.

        """

        self.filtered_element_ids = [ range(len(self.tree)) ]
        for filter in self.filters:
            new_filtered_elements = [i for i, e in enumerate(self.tree)
                                     if i in self.filtered_element_ids[-1] and
                                        filter.element_passes_filter(e)]
            self.filtered_element_ids.append(new_filtered_elements)

    def as_html(self, filtered = False, html_frame = True):
        """Return the search result in a html page.

        Parameters
        ----------
        filtered : bool
            To know if the search if filtered or not.
        html_frame: bool
            Set or not the an html frame.

        Returns
        -------
        html = str
            Html page.

        """

        html = ""
        if html_frame:
            html = "<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" /></head><body>\n"
        for i, element in enumerate(self.tree):
            if filtered and i not in self.filtered_element_ids[-1]:
                continue
            html += "<table>\n"
            table = [dict() for _ in range(len(
                self.structure_type_handler.flat_data_hierarchy))]
            self._element_as_table(
                element, self.structure_type_handler.data_hierarchy, table, 0)
            #print table
            for j, row in enumerate(table):
                html += "<tr>\n"
                if j == 0:
                    html += "<td rowspan=\"{0}\" "\
                            "class=\"element_id\">{1}</td>\n".format(
                        len(self.structure_type_handler.flat_data_hierarchy), i)
                html += "<td class=\"ann_type\">{0}</td>".format(
                    self.structure_type_handler.flat_data_hierarchy[j])
                for _, column in sorted(row.items(), key=operator.itemgetter(0)):
                    html += "<td colspan=\"{0}\" class=\"{2}\">{1}</td>\n".format(
                        column[1], column[0],
                        self.structure_type_handler.flat_data_hierarchy[j])
                html += "</tr>\n"
            html += "</table>\n"
        if html_frame:
            html += "</body></html>"
        return html

    def _element_as_table(self, elements, hierarchy, table, column):
        """Insert an element into a table.

        Parameters
        ----------
        elements : array_like
            An array with the elements.
        hierarchy: array_like
            An array with the data structure hierarchy.
        table : array_like
            Table number.
        column: int
            Column number.

        Returns
        -------
        inserted : int
            Number of elements inserted.

        """

        inserted = 0
        for i, t in enumerate(hierarchy):
            if type(t) is list:
                elements_list = elements[i]
                for i, e in enumerate(elements_list):
                    inserted += self._element_as_table(
                        e, t, table, column + i + inserted)
                inserted = inserted + len(elements_list) - 1
                merge_rows = [ r for r in hierarchy if type(r) is not list]
                for r in merge_rows:
                    row = self.structure_type_handler.flat_data_hierarchy.index(r)
                    if column in table[row]:
                        table[row][column] = (table[row][column][0], inserted + 1)
                    else:
                        table[row][column] = ("", inserted + 1)
            else:
                row = self.structure_type_handler.flat_data_hierarchy.index(t)
                a = elements[i]["annotation"]
                if a == "":
                    a = "&nbsp;"
                    #if (column + 1) > len(table[row]):
                if column in table[row]:
                    table[row][column] = (a, table[row][column][1])
                else:
                    table[row][column] = (a, 1)

        return inserted

    def _range_for_string_in_utterance(self, string, utterance, start_at_pos=0):
        """Calculates the regions of the string to
        search in the main string.

        Parameters
        ----------
        string : str
            String to search.
        utterance : str
            Main string to make the search on it.
        start_pos : int
            Gives the start position to search the regions.

        Returns
        -------
        return : tuple
            Return a tuple with the regions.

        """

        start_string = ""
        end_string = ""
        nonword_at_start = re.match("\W+", string)
        if nonword_at_start:
            start_string = nonword_at_start.group(0)
            string = string[nonword_at_start.end(0):]

        nonword_at_end = re.search("\W+$", string)
        if nonword_at_end:
            end_string = nonword_at_end.group(0)
            string = string[:nonword_at_end.start(0)]

        s = re.compile("{0}\\b{1}\\b{2}".format(re.escape(start_string),
            re.escape(string), re.escape(end_string)), re.I)
        m = s.search(utterance, start_at_pos)

        if m:
            #self.last_position = m.end(0)
            return (m.start(0), m.end(0))
        else:
            return None

    def update_elements_with_ranges(self, search_tier, update_tiers):
        """Updated the already existing elements in
        the Annotation Tree with regions. The regions
        are the positions values of the words in the
        raw text.

        Parameters
        ----------
        search_tier : str
            The name of the first element in the hierarchy.
        update_tiers : array_like
            An array with the elements that search will focus.

        """

        start_pos = dict()
        for element in self.tree:
            for tier in update_tiers:
                start_pos[tier] = 0
            self._update_with_ranges(element, self.structure_type_handler
            .data_hierarchy, search_tier, update_tiers, start_pos, "")

    def _update_with_ranges(self, elements, hierarchy, search_tier,
                            update_tiers, start_pos, string_to_search):
        """Run through all the values in one
        element of the Annotation Tree to
        update the regions.

        Parameters
        ----------
        elements : array_like
            An array with the elements.
        hierarchy: array_like
            An array with the data structure hierarchy.
        search_tier : str
            The name of the first element in the hierarchy.
        update_tiers : array_like
            An array with the elements that search will focus.
        start_pos : int
            Gives the start position to search the regions.
        string_to_search : str
            String to search.

        """

        for i, t in enumerate(hierarchy):
            if type(t) is list:
                elements_list = elements[i]
                for i, e in enumerate(elements_list):
                    self._update_with_ranges(
                        e, t, search_tier, update_tiers, start_pos,
                        string_to_search)
            else:
                if t == search_tier:
                    string_to_search = elements[i]['annotation']
                elif t in update_tiers:
                    if elements[i]['annotation'] != "":
                        region = self._range_for_string_in_utterance(
                            elements[i]['annotation'], string_to_search,
                            start_pos[t])
                        if not region:
                            raise RegionNotFoundInString(
                                "String '{0}' not found in '{1}'.".format(
                                    elements[i]['annotation'], string_to_search))
                        for tier in start_pos:
                            if region[0] > start_pos[tier]:
                                start_pos[tier] = region[0]
                        elements[i]['region'] = region
                        start_pos[t] = region[1]


class AnnotationTreeFilter():
    """
    AnnotationTreeFilter tree-like structure constructor.

    The main objective of this class is to make it possible
    to make searches in the AnnotationTree.

    """
    (AND, OR)  = range(2)

    def __init__(self, data_structure_type):
        """Class constructor.

        """

        self.structure_type_handler = data_structure_type
#        if isinstance(data_structure_type, data.DataStructureType):
#            self.structure_type_handler = data.DataStructureTypeGraid()
#        else:
#            raise(
#                data.DataStructureTypeNotSupportedError(
#                    "Data structure type {0} not supported".format(
#                        data_structure_type)))

        self.filter = dict()
        for e in self.structure_type_handler.flat_data_hierarchy:
            self.filter[e] = ""

        self.reset_match_object()
        self.inverted = False
        self.boolean_operation = self.AND
        self.contained_matches = False

    def reset_match_object(self):
        """Reset a match object.

        """

        self.matchobject = dict()
        for e in self.structure_type_handler.flat_data_hierarchy:
            self.matchobject[e] = dict()

    def set_filter_for_type(self, ann_type, filter_string):
        """Set a filter for a given type.

        Parameters
        ----------
        ann_type : str
            Value of the field in the data structure hierarchy.
        filter_string: str
            String of the filter.

        """

        self.filter[ann_type] = filter_string

    def set_inverted_filter(self, inverted):
        """Set the inverted value to a filter.

        Parameters
        ----------
        inverted : bool

        """

        self.inverted = inverted

    def set_contained_matches(self, contained_matches):
        """Set the contained matches for a filter.

        Parameters
        ----------
        contained_matches : bool

        """

        self.contained_matches = contained_matches

    def set_boolean_operation(self, type):
        """Set the operation type to the filter.

        Parameters
        ----------
        type : str
            Could be AND or OR

        """

        self.boolean_operation = type

    def element_passes_filter(self, element):
        """Verify if a specific element passes in through a filter.

        Parameters
        ----------
        element : array_like
            An array of string values.

        Returns
        -------
        passed : bool
            Passes or not.

        See also
        --------
        _passes_filter

        """

        # is there a filter defined?
        all_filter_empty = True
        for ann_type in self.filter.keys():
            if self.filter[ann_type] != "":
                all_filter_empty = False
        if all_filter_empty:
            return True

        if self.boolean_operation == self.AND:
            passed = True
        else:
            passed = False

        passed = self._passes_filter(passed, element, self.structure_type_handler.data_hierarchy)

        if self.inverted:
            passed = not passed

        return passed

    def _passes_filter(self, passed, elements, hierarchy):
        """Verify if a specific element passes in through a filter.

        Parameters
        ----------
        passed : bool
            Passes or not.
        elements : array_like
            An array of string values.
        hirerarchy : array_like
            Structure of the array.

        Returns
        -------
        passed : bool
            Passes or not.

        """

        for i, t in enumerate(hierarchy):
            if type(t) is list:
                elements_list = elements[i]
                local_passes = False
                for i, e in enumerate(elements_list):
                    passes = self._passes_filter(passed, e, t)
                    local_passes = (local_passes or passes)

                if self.boolean_operation == self.AND:
                    passed = (passed and local_passes)
                else:
                    passed = (passed or local_passes)
            else:
                passes = False
                if self.filter[t] != "":
                    match = re.search(
                        self.filter[t], elements[i]["annotation"])
                    if match:
                        self.matchobject[t][elements[i]["id"]] =\
                        [ [m.start(), m.end()] for m in re.finditer(
                            self.filter[t], elements[i]["annotation"]) ]
                        passes = True
                elif self.boolean_operation == self.AND:
                    passes = True

                if self.boolean_operation == self.AND:
                    passed = (passed and passes)
                else:
                    passed = (passed or passes)

        return passed