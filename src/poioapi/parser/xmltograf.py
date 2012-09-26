# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT

import os
import re
from graf.PyGrafRenderer import PyGrafRenderer
from graf.PyGraph import PyGraph

from graf.PyGraphParser import PyGraphParser
from nltk.corpus.reader.api import CorpusReader
from nltk.corpus.reader.util import StreamBackedCorpusView

class TestGrAF(CorpusReader):

    CorpusView = StreamBackedCorpusView

    def __init__(self, filepath):
        self.filepath = filepath.replace('pickle','txt')
        self._cur_file = ""
        self._cur_offsets = []
        self._char_to_byte = {}
        self._byte_to_char = {}
        self._file_end = 0
        self._graph = None

        CorpusReader.__init__(self, os.path.dirname(filepath),
           '(?!\\.).*\\.txt', 'utf-8')

    def _read_block(self, stream, file_ending, label):
        """
        Generic method for retrieving annotated text from a file stream.
        @type stream: SeekableUnicodeStreamReader
        @param stream: file stream from StreamBackedCorpusView in
                       corpus/reader/util.py
        @type file_ending: C{str}
        @param file_ending: xml annotation file containing annotation
                            offsets
        @type label: C{str}
        @param label: label of requested annotation
        @return: list of annotated text from a block of the file stream
        @rtype: C{list} of C{str}
        """

        file = self._get_basename(stream.name) + file_ending
        if file != self._cur_file:
            self._cur_file = file
            offsets = self._get_annotation(file, label)
            self._cur_offsets = offsets
            self._get_disc(stream)
            char_to_byte = self._char_to_byte
            byte_to_char = self._byte_to_char
        else:
            offsets = self._cur_offsets
            char_to_byte = self._char_to_byte
            byte_to_char = self._byte_to_char
        slimit = stream.tell()
        offset_slimit = byte_to_char.get(slimit, slimit)
        offset_elimit = offset_slimit + 500

        subset = self._get_subset(offsets, offset_slimit, offset_elimit)

        read_size = (self._get_read_size(subset, char_to_byte, slimit,
            offset_elimit))

        text = stream.read(read_size)

        block = self._get_block(subset, text, offset_slimit)
        return block

    def _get_basename(self, file):
        """
        @type file: C{str}
        @param file: full filename
        @return: the basename of the specified file
        @rtype: C{str}
        """

        return file[0:len(file)-4]

    def _get_disc(self, stream):
        """
        Using the specified file stream, this method creates two
        discrepency mappings, both as dictionaries:
            1. self._char_to_byte uses key = character number,
                                       entry = byte number
            2. self._byte_to_char uses key = byte number,
                                       entry = character number
        @type stream: StreamBackedCorpusView
        @param stream: file stream
        """

        self._char_to_byte = {}
        self._byte_to_char = {}
        stream.read()
        file_end = stream.tell()
        self._file_end = file_end
        stream.seek(0)
        for i in range(file_end+1):
            if i != stream.tell():
                self._char_to_byte[i] = stream.tell()
                self._byte_to_char[stream.tell()] = i
            stream.read(1)
        stream.seek(0)

    def _get_subset(self, offsets, offsets_start, offsets_end):
        """
        @type offsets: C{list} of C{int} pairs
        @param offsets: List of all offsets
        @type offsets_start: C{int}
        @param offsets_start: start of requested set of offsets
        @type offsets_end: C{int}
        @param offsets_end: end of requested set of offsets
        @return: a list of all offsets between offsets_start and offset_end
        @rtype: C{list} of C{str}
        """

        subset = []
        for i in offsets:
            if (i[0] >= offsets_start and i[1] <= offsets_end and
                i[0] != i[1]):
                subset.append(i)
            elif (i[0] >= offsets_start and i[1] > offsets_end and
                  i[0] != i[1] and i[0] <= offsets_end):
                subset.append(i)
        return subset

    def _get_read_size(self, subset, char_to_byte, slimit, offset_end):
        """
        @return: the byte size of text that should be read
        next from the file stream
        @rtype: C{int}
        """

        if len(subset) != 0:
            last1 = subset[len(subset)-1]
            last = last1[1]
            last = char_to_byte.get(last, last)
            read_size = last - slimit
        else:
            elimit = char_to_byte.get(offset_end, offset_end)
            read_size = elimit - slimit
        return read_size

    def _get_block(self, subset, text, offsets_start):
        """
        Retrieve the annotated text, annotations are contained in subset
        @type subset: C{list}
        @param subset: list of annotation offset pairs
        @type text: C{str}
        @param text: text read from text stream
        @type offsets_start: C{int}
        @param offset_start: integer to correct for discrepency
                            between offsets and text character number
        @return: list of annotated text
        @rtype: C{list} of C{str}
        """

        block = []
        for s in subset:
            start = s[0] - offsets_start
            end = s[1] - offsets_start
            chunk = text[start:end].encode('utf-8')
            chunk = self._remove_ws(chunk)
            block.append(chunk)
        return block

    def _read_block(self, stream, file_ending, label):
        """
        Generic method for retrieving annotated text from a file stream.
        @type stream: SeekableUnicodeStreamReader
        @param stream: file stream from StreamBackedCorpusView in
                       corpus/reader/util.py
        @type file_ending: C{str}
        @param file_ending: xml annotation file containing annotation
                            offsets
        @type label: C{str}
        @param label: label of requested annotation
        @return: list of annotated text from a block of the file stream
        @rtype: C{list} of C{str}
        """
        file = self._get_basename(stream.name) + file_ending
        if file != self._cur_file:
            self._cur_file = file
            offsets = self._get_annotation(file, label)
            self._cur_offsets = offsets
            self._get_disc(stream)
            char_to_byte = self._char_to_byte
            byte_to_char = self._byte_to_char
        else:
            offsets = self._cur_offsets
            char_to_byte = self._char_to_byte
            byte_to_char = self._byte_to_char
        slimit = stream.tell()
        offset_slimit = byte_to_char.get(slimit, slimit)
        offset_elimit = offset_slimit + 500

        subset = self._get_subset(offsets, offset_slimit, offset_elimit)

        read_size = (self._get_read_size(subset, char_to_byte, slimit,
            offset_elimit))

        text = stream.read(read_size)

        block = self._get_block(subset, text, offset_slimit)
        return block

    def _get_annotation(self, annfile, label):
        """
        Parses the given annfile and returns the offsets of all
        annotations of type 'label'

        @type annfile: C{str}
        @param annfile: xml file containing annotation offsets
        @type label: C{str}
        @param label: annotation type label
        @return: list of annotation offsets
        @rtype: C{list} of C{pairs} of C{int}
        """
        parser = PyGraphParser()
        g = parser.parse(annfile)

        self._graph = g

        node_list = g.nodes()

        offsets = []

        for node in node_list:
            pair = self._add_annotations(node, label)
            offsets.extend(pair)

        offsets.sort()
        return offsets

    def _add_annotations(self, node, label):
        """
        Given a node and annotation label, this method calls
        _get_offsets for each annotation contained by node,
        and adds them to the return list if they are oftype 'label'

        @type node: C{PyNode}
        @param node: a node in the Graf graph
        @type label: C{str}
        @param label: annotation type label
        @return: the annotation offsets of type 'label'
                 contained by the specified node
        @rtype: C{list} of C{pairs} of C{int}
        """
        node_offsets = []
        for a in node._annotations:
            if a._label == label:
                pair = self._get_offsets(node)
                if pair is not None:
                    pair.sort()
                    node_offsets.append(pair)
        return node_offsets

    def _get_offsets(self, node):
        """
        @type node: C{PyNode}
        @param node: a node in the Graf graph
        @return: the offsets contained by a given node
        @rtype: C{pair} of C{int}, or C{None}
        """

        if len(node._links) == 0 and node._outEdgeList != []:
            offsets = []
            edge_list = node._outEdgeList
            edge_list.reverse()
            for edge in edge_list:
                temp_offsets = self._get_offsets(edge._toNode)
                if temp_offsets is not None:
                    offsets.extend(self._get_offsets(edge._toNode))
            if len(offsets) == 0:
                return None
            offsets.sort()
            start = offsets[0]
            end = offsets[len(offsets)-1]
            return [start, end]
        elif len(node._links) != 0:
            offsets = []
            for link in node._links:
                for region in link._regions:
                    for anchor in region._anchors:
                        offsets.append(int(anchor._offset))
            offsets.sort()
            start = offsets[0]
            end = offsets[len(offsets)-1]
            return [start, end]
        else:
            return None

    def _remove_ws(self, chunk):
        """
        @return: string of text from chunk without end line characters
        and multiple spaces
        @rtype: C{str}
        """
        chunk = chunk.replace("\n", "")
        words = chunk.split()
        new_str = ""
        for i in words:
            if i == words[len(words)-1]:
                new_str += i
            else:
                new_str = new_str + i + " "
        return new_str

    def create_graf(self):
        # Rendering the Graph

        graf_render = PyGrafRenderer(self.filepath + '-rend.xml')
        graf_render.render(self._graph)

    def _read_wfw_block(self, stream):
        return self._read_block(stream, '-wfw.xml', 'wfw')

    def get_wfw(self):

        for wfw in (self.CorpusView(self.filepath,
            self._read_wfw_block,encoding='utf-8')):
            print(wfw)

    def _read_graid1_block(self, stream):
        return self._read_block(stream, '-graid1.xml', 'graid1')

    def get_graid1(self):

        for graid1 in (self.CorpusView(self.filepath,
            self._read_graid1_block,encoding='utf-8')):
            print(graid1)

    def _read_graid2_block(self, stream):
        return self._read_block(stream, '-graid2.xml', 'graid2')

    def get_graid2(self):

        for graid2 in (self.CorpusView(self.filepath,
            self._read_graid2_block,encoding='utf-8')):
            print(graid2)

    def _read_trans_block(self, stream):
        return self._read_block(stream, '-trans.xml', 'trans')

    def get_trans(self):

        for trans in (self.CorpusView(self.filepath,
            self._read_trans_block,encoding='utf-8')):
            print(trans)