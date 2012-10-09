# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
""" This module is to test all the parsing modules
and methods that PoioAPI parser uses. Including the
parser to the three data hierarchies, GRAID,
MORPHSYN and WORD.

Note: This module it'll test the modules that
generates a XML file.
In order to drive this test the pickle file used is
the Balochi Text1.pickle.
"""

from poioapi import data, annotationtree

import os
import pickle
import comment
import xmltoanntree
import xmltograf
import search_replace

class TestCreateElementFile:
    """
    This class contain the test methods to the classes
    that parse the elements from a data structure
    hierarchy to a XML file which means to the GrAF.

    The test describe in this class can be used for the
    parsing of comments, translation and the creation of
    the raw file. Although is need to change some of
    the code lines. Thoses lines are the file_parsed is
    need to change the suffix to e. g. '-translation'.
    This is because of the retrieving process of the
    data hierarchy structures be identical in the three
    existing ones.
    The same will work to the rest of the elements in the
    data hierarchy. E. g. in Morph data structure the
    element word will generate a file with a suffix '-word'
    to the original file name or in GRAID structure graid1
    generate a '-graid1' suffix.

    Note: Is important to know that the suffix depends
    on the names that the structures of the Annotation Tree
    have.

    See Also
    --------
    poioapi.data : Module that contains the data structures of
                   a Annotation Tree.

    """

    def test_create_element_xml(self):
        """Raise an assertion if can't retrieve the file.

        Return given file as a single string.

        Raises
        ------
        AssertionError
            If can't retrieve a string.

        """

        # Initialize values
        filepath = '/home/alopes/tests/Balochi Text1.pickle'

        comment.CreateCommentFile(filepath).create_cmts_xml()

        # The result must be Balochi Text1-comment.xml because
        # of the create_cmts_xml it'll add the
        # sufix -comment to the original file name.

        # Open the file
        basename = filepath.split('.pickle')
        file_parsed = os.path.abspath(basename[0]
                                      + '-comment' + '.xml')
        xml_file = open(file_parsed, 'r')

        # Getting the xml content
        xml_content = xml_file.readlines()

        xml_file.close()

        # Opening the expected file result
        file_result = os.path.dirname(__file__) + '/sample_files/' \
                      + 'comment' + '.xml'
        xml_file = open(file_result, 'r')

        # Getting the xml content
        expected_result = xml_file.readlines()

        xml_file.close()

        assert(xml_content == expected_result)

class TestXmlToAnnTree:
    """
    Class that test the parsing of the GrAF files to
    the Annotation Tree format.

    See Also
    --------
    poioapi.data : Module that contains the data structures of
                   a Annotation Tree.
    poioapi.annotationtree : Module that contains the instance
                             of a Annotation Tree.

    """

    def test_graid_hierarchy(self):
        """Raise an assertion if can't retrieve the file.

        The file that result's from the parsing is
        complemented by the suffix '-graid.pickle'.

        Return given file as a single string.

        Raises
        ------
        AssertionError
            If can't retrieve a string.

        """

        # Initialize values
        filepath = '/home/alopes/tests/Balochi Text1.pickle'

        annotation_tree = annotationtree.AnnotationTree(data.GRAID)
        annotation_tree_res = annotationtree.AnnotationTree(data.GRAID)

        # Parsing the file
        xmltotree = xmltoanntree.XmlToAnnTree()
        xmltotree.graid_hierarchy(filepath)

        # After the parsing should result a file that
        # contains the Annotation Tree retrieved from
        # the GrAF files.

        # Open the original file and then load the
        # Annotation Tree generated
        filepath = filepath.replace('.pickle', '-graid.pickle')
        file = open(filepath, 'rb')
        annotation_tree.tree = pickle.load(file)

        # Opening the expected file result
        file_result = os.path.dirname(__file__) + '/sample_files/'\
                      + 'parsed-graid.pickle'

        # Open the expected file and then load the
        # Annotation Tree generated
        filer = open(file_result, 'rb')
        annotation_tree_res.tree = pickle.load(filer)

        # Auxiliary to the assert method
        result = True

        for original, result in zip(annotation_tree.elements(),
            annotation_tree_res.elements()):
            if original != result:
                result = False
                break

        assert result

    def test_morph_hierarchy(self):
        """Raise an assertion if can't retrieve the file.

        The file that result's from the parsing is
        complemented by the suffix '-morph.pickle'.

        Return given file as a single string.

        Raises
        ------
        AssertionError
            If can't retrieve a string.

        """

        # Initialize values
        filepath = '/home/alopes/tests/Balochi Text1.pickle'

        annotation_tree = annotationtree.AnnotationTree(data.MORPHSYNT)
        annotation_tree_res = annotationtree.AnnotationTree(data.MORPHSYNT)

        # Parsing the file
        xmltotree = xmltoanntree.XmlToAnnTree()
        xmltotree.graid_hierarchy(filepath)

        # After the parsing should result a file that
        # contains the Annotation Tree retrieved from
        # the GrAF files.

        # Open the original file and then load the
        # Annotation Tree generated
        filepath = filepath.replace('.pickle', '-morph.pickle')
        file = open(filepath, 'rb')
        annotation_tree.tree = pickle.load(file)

        # Opening the expected file result
        file_result = os.path.dirname(__file__) + '/sample_files/'\
        + 'parsed-morph.pickle'

        # Open the expected file and then load the
        # Annotation Tree generated
        filer = open(file_result, 'rb')
        annotation_tree_res.tree = pickle.load(filer)

        # Auxiliary to the assert method
        result = True

        for original, result in zip(annotation_tree.elements(),
            annotation_tree_res.elements()):
            if original != result:
                result = False
                break

        assert result

    def test_word_hierarchy(self):
        """Raise an assertion if can't retrieve the file.

        The file that result's from the parsing is
        complemented by the suffix '-word.pickle'.

        Return given file as a single string.

        Raises
        ------
        AssertionError
            If can't retrieve a string.

        """

        # Initialize values
        filepath = '/home/alopes/tests/Balochi Text1.pickle'

        annotation_tree = annotationtree.AnnotationTree(data.WORDS)
        annotation_tree_res = annotationtree.AnnotationTree(data.WORDS)

        # Parsing the file
        xmltotree = xmltoanntree.XmlToAnnTree()
        xmltotree.graid_hierarchy(filepath)

        # After the parsing should result a file that
        # contains the Annotation Tree retrieved from
        # the GrAF files.

        # Open the original file and then load the
        # Annotation Tree generated
        filepath = filepath.replace('.pickle', '-word.pickle')
        file = open(filepath, 'rb')
        annotation_tree.tree = pickle.load(file)

        # Opening the expected file result
        file_result = os.path.dirname(__file__) + '/sample_files/'\
        + 'parsed-word.pickle'

        # Open the expected file and then load the
        # Annotation Tree generated
        filer = open(file_result, 'rb')
        annotation_tree_res.tree = pickle.load(filer)

        # Auxiliary to the assert method
        result = True

        for original, result in zip(annotation_tree.elements(),
            annotation_tree_res.elements()):
            if original != result:
                result = False
                break

        assert result

class TestRendToGrAF:
    """
    Class that test the rendering the files from the
    Annotation Tree to GrAF.

    The file to be rendering is generate according to
    a given type. The type is the the element in data
    structure hierarchy. For example the elements in
    the GRAID structure are WFW, graid1, graid2, etc,
    this are the element that will rendered.

    Note: Is important to know that the rendering is
    is done with the help of the Graf-python.
    """

    def test_parse_xml_graf(self):
        """Raise an assertion if can't retrieve the file.

        The file that result's from the parsing is
        complemented by the suffix '-rend.xml'.
        This example test will use the GRAID hierarchy and
        the rendered file will be generated with the 'wfw'
        type.

        Return given file as a single string.

        Raises
        ------
        AssertionError
            If can't retrieve a string.

        """

        # Initialize values
        filepath = '/home/alopes/tests/Balochi Text1.pickle'


        # XML (in GrAF) to AnnotationTree and the
        # result must be Balochi Text1-rend.xml
        xmltoann = xmltoanntree.XmlToAnnTree()
        xmltoann.graid_hierarchy(filepath)

        # Initialize the GrAF parser
        graf = xmltograf.RendToGrAF(filepath)

        # Choose a type of GrAF Graid1/2, WfW or Gloss
        # in our case the 'wfw'
        graf.parse_xml_graf('wfw')

        # Open the file
        basename = filepath.split('.pickle')
        file_parsed = os.path.abspath(basename[0]
                                      + '-rend' + '.xml')
        xml_file = open(file_parsed, 'r')

        # Getting the xml content
        xml_content = xml_file.readlines()

        xml_file.close()

        # Opening the expected file result
        file_result = os.path.dirname(__file__) + '/sample_files/'\
                      + 'rend' + '.xml'
        xml_file = open(file_result, 'r')

        # Getting the xml content
        expected_result = xml_file.readlines()

        xml_file.close()

        assert(xml_content == expected_result)

class TestSearchReplace:
    """
    Class that test the possibility to search and replace
    in the XML GrAF file.

    The test will be done upon the results generated by
    the method that parses to XML to GrAF. The files will
    be as base the 'wfw' elements. So every results of
    the search will on the file rend.xml in sample_files
    folder.

    See Also
    --------
    test_parse_xml_graf : Parsing XML to GrAF.

    """

    def test_find_word(self):
        """Raise an assertion if can't element.

        The result of a finding is an list of elements.
        Depending in the parameters. There are two:
        case_sensitive is to find the exact word and
        whole_word is to find the word in sentences or
        words.
        In this test case will use the whole_word parameter
        as True.

        Return element of the list.

        Raises
        ------
        AssertionError
            If can't retrieve a string.

        See Also
        --------
        poioapi.parser.search_replace.find_word : Here is more
        information about the find_word parameters.

        """

        # Initialize values
        filepath = os.path.dirname(__file__) + '/sample_files/'\
                   + 'rend' + '.xml'

        search = search_replace.SearchReplace(filepath)

        # The test will try to find the word in the XML files.
        # The word to find will be 'SUB'.
        searchs = search.find_word('SUB',False,True)

        for sea in searchs:
            result = sea[0]+' - '+sea[1]
            break

        result_expected = 'Ref node: wfw-n116 - ' \
                          'Number of hits per line: 1'

        assert(result_expected == result)

    def test_replace_word(self):
        """Raise an assertion if can't retrieve element.

        This test case is to find a specific word and then
        replace it. To see the results will use the
        find_word method from the same module.
        To run this method is need to give the reference node.
        This reference is in the GrAF file and it's the link
        to the word, clause unit or other element in the data
        structure hierarchy.

        Return element of the list.

        Raises
        ------
        AssertionError
            If can't retrieve a string.

        See Also
        --------
        poioapi.parser.search_replace.find_word : Here is more
        information about the find_word parameters.

        """

        # Initialize values
        filepath = os.path.dirname(__file__) + '/sample_files/'\
                   + 'rends' + '.xml'

        search = search_replace.SearchReplace(filepath)

        # Replace the exact word in the node 339 by the new word
        search.replace_word('SUB','NEWORD','wfw-n339')

        # Try to fin the new word 'NEWORD'
        searchs = search.find_word('NEWORD',False,True)

        for sea in searchs:
            result = sea[0]+' - '+sea[1]
            break

        result_expected = 'Ref node: wfw-n339 - '\
                          'Number of hits per line: 1'

        assert(result_expected == result)

    def test_replace_all(self):
        """Raise an assertion if can't retrieve element.

        This test case is to find the words and replace it
        by the new one.

        Return element of the list.

        Raises
        ------
        AssertionError
            If can't retrieve a string.

        See Also
        --------
        poioapi.parser.search_replace.find_word : Here is more
        information about the find_word parameters.

        """

        # Initialize values
        filepath = os.path.dirname(__file__) + '/sample_files/'\
                   + 'rendsa' + '.xml'

        search = search_replace.SearchReplace(filepath)

        # Replace the exact word that finds and replace by
        # the new word
        search.replace_all('SUB','NEWORD')

        # Try to fin the new word 'NEWORD'
        searchs = search.find_word('NEWORD',False,True)

        for sea in searchs:
            result = sea[0]+' - '+sea[1]
            break

        result_expected = 'Ref node: wfw-n116 - '\
                          'Number of hits per line: 1'

        assert(result_expected == result)