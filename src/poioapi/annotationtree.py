# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: Peter Bouda <pbouda@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
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
import re
from poioapi import data


import pickle
import regex
import operator

class AnnotationTree():
    """
    AnnotationTree tree-like structure 
    constructor.

    """

    def __init__(self, data_structure_type):
        """Class's constructor.....

        """

        self.tree = []
        self._next_annotation_id = 0

        self.data_structure_type = data_structure_type

        if data_structure_type == data.GRAID:
            self.structure_type_handler = data.DataStructureTypeGraid()
        elif data_structure_type == data.MORPHSYNT:
            self.structure_type_handler = data.DataStructureTypeMorphsynt()

        self.filters = []
        self.filtered_element_ids = [[]]

    @property
    def next_annotation_id(self):
        """Returns the next annotation id.

        Returns
        -------
        _next_annotation_id : int
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

        file = open(filepath, "rb")
        self.tree = pickle.load(file)
        file.close()

    def save_tree_as_graf(self, filepath):
        """Save the project into the GrAF
        specifications.

        Parameters
        ----------
        filepath : str
            The absolute path to a file.

        """

        graf.Parser(filepath).parsing(self.data_structure_type, self.tree)

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
            return AnnotationTreeFilter(self.data_structure_type)

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
                self.data_structure_type.flat_data_hierarchy))]
            self._element_as_table(
                element, self.data_structure_type.data_hierarchy, table, 0)
            #print table
            for j, row in enumerate(table):
                html += "<tr>\n"
                if j == 0:
                    html += "<td rowspan=\"{0}\" "\
                            "class=\"element_id\">{1}</td>\n".format(
                        len(self.data_structure_type.flat_data_hierarchy), i)
                html += "<td class=\"ann_type\">{0}</td>".format(
                    self.data_structure_type.flat_data_hierarchy[j])
                for _, column in sorted(row.items(), key=operator.itemgetter(0)):
                    html += "<td colspan=\"{0}\" class=\"{2}\">{1}</td>\n".format(
                        column[1], column[0],
                        self.data_structure_type.flat_data_hierarchy[j])
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
        inserted = int
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
                    row = self.data_structure_type.flat_data_hierarchy.index(r)
                    if column in table[row]:
                        table[row][column] = (table[row][column][0], inserted + 1)
                    else:
                        table[row][column] = ("", inserted + 1)
            else:
                row = self.data_structure_type.flat_data_hierarchy.index(t)
                a = elements[i]["annotation"]
                if a == "":
                    a = "&nbsp;"
                #if (column + 1) > len(table[row]):
                if column in table[row]:
                    table[row][column] = (a, table[row][column][1])
                else:
                    table[row][column] = (a, 1)

        return inserted

    def _range_for_word_in_utterance(self, word, utterance, start_at_pos=0):
        self.last_position = 0

        s = re.compile("\\b{0}\\b".format(word))
        m = s.search(utterance, start_at_pos)
        if m:
            self.last_position = m.end(0)
            return (m.start(0), m.end(0))
        else:
            return None


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

        self.data_structure_type = data_structure_type
        if data_structure_type == data.GRAID:
            self.structure_type_handler = data.DataStructureTypeGraid()

        self.filter = dict()
        for e in self.data_structure_type.flat_data_hierarchy:
            self.filter[e] = ""

        self.reset_match_object()
        self.inverted = False
        self.boolean_operation = self.AND
        self.contained_matches = False

    def reset_match_object(self):
        """Reset a match object.

        """

        self.matchobject = dict()
        for e in self.data_structure_type.flat_data_hierarchy:
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

        #if self.filter["utterance"] == "" and self.filter["translation"] == "" and self.filter["word"] == "" and self.filter["morpheme"] == "" and self.filter["gloss"] == "":
        #    return True

        if self.boolean_operation == self.AND:
            passed = True
        else:
            passed = False

        passed = self._passes_filter(passed, element, self.data_structure_type.data_hierarchy)

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
                    match = regex.search(
                        self.filter[t], elements[i]["annotation"])
                    if match:
                        self.matchobject[t][elements[i]["id"]] = \
                            [ [m.start(), m.end()] for m in regex.finditer(
                                self.filter[t], elements[i]["annotation"]) ]
                        passes = True
                elif self.boolean_operation == self.AND:
                    passes = True

                if self.boolean_operation == self.AND:
                    passed = (passed and passes)
                else:
                    passed = (passed or passes)

        return passed

