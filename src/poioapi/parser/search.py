# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
""" This module is to make the search in the
GrAF files.

"""

from xml.dom import minidom

import codecs

class SearchReplace:
    """
    Class that allows to search and replace
    in the XML GrAF file.

    """

    def __init__(self, filepath):
        """Class's constructor.

        Parameters
        ----------
        filepath : str
            Path of the file to manipulate.

        """

        self.filepath = filepath
        self.word = ''
        self.xml = minidom.parse(filepath)

    def find_word(self, word, case_sensitive = True, whole_word = False):
        """This method look for the given reference node to
        replace the word by the new word.

        Parameters
        ----------
        word : str
            Word to be find.
        case_sensitive : bool
            Is to find the exact word.
        whole_word : bool
            Find the word in sentences or words.

        """

        result_list = []
        hits = 0

        for ann in self.xml.getElementsByTagName('a'):
            attr = ann.getAttribute('ref')

            for node in ann.getElementsByTagName('f'):
                value = node.firstChild.nodeValue

                if case_sensitive:
                    if value == word:
                        hits+=1
                elif whole_word:
                    try:
                        for val in value.split(word):
                            hits+=1
                        hits-=1
                    except AttributeError as attr_error:
                        print(attr_error)

            if hits > 0:
                aux_list = ('Ref node: ' + str(attr),
                            'Number of hits per line: ' + str(hits))
                result_list.append(aux_list)
                hits = 0

        return result_list

    def replace_word(self, word, new_word, ref_node):
        """This method look for the given reference node to
        replace the word by the new word.

        Parameters
        ----------
        word : str
            Word to be replaced.
        new_word : str
            Word to replace the one that is being searched.
        ref_node : str
            Reference to the node that contains the word to be replaced.

        """

        for ann in self.xml.getElementsByTagName('a'):
            attr = ann.getAttribute('ref')

            if attr == ref_node:
                for node in ann.getElementsByTagName('f'):
                    value = node.firstChild.nodeValue

                    if value == word:
                        node.firstChild.nodeValue = new_word
                        self._write_file()

    def replace_all(self, word, new_word):
        """This method look for the given word in all the
        feature tags and then replace it by the new word.

        Parameters
        ----------
        word : str
            Word to be replaced.
        new_word : str
            Word to replace the one that is being searched.

        """

        for ann in self.xml.getElementsByTagName('a'):
            attr = ann.getAttribute('ref')

            for node in ann.getElementsByTagName('f'):
                value = node.firstChild.nodeValue

                if value == word:
                    node.firstChild.nodeValue = new_word
                    self._write_file()

    def _write_file(self):
        """Method that will write the changes in the
        XML file.

        """

        file = codecs.open(self.filepath,'w', 'utf-8')
        file.write(self.xml.toxml())
        file.close()
