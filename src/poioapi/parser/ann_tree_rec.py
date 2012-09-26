# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
""" This module is to create the raw txt
file form the pickle file
"""
import codecs
from poioapi import annotationtree
from poioapi import data
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from xml.dom import minidom

import pickle
import os

class XmlHandler(ContentHandler):

    def __init__(self):
        self.tokenizer = []
        self.token_id = []
        self.regions = []

    def startElement(self, name, attrs):
        if name == 'region':
            id = attrs.getValue('xml:id')
            att = attrs.getValue('anchors')
            tokenizer = att.split()
            self.tokenizer.append(tokenizer)
            id = id.split('-r')
            self.token_id.append(id[1])
        if name == 'link':
            att = attrs.getValue('targets')
            tokenizer = att.split('-r')
            self.tokenizer.append(tokenizer[1])


    def characters (self, ch):
        return

    def endElement(self, name):
        return

    def get_tokenizer(self):
        return self.tokenizer

    def get_token_id(self):
        return self.token_id

class ProcessContent:

    def __init__(self, restoreMetaFile):
        self.tokenizer = []
        self.token_id = []
        self.restoreMetaFile = restoreMetaFile

    def process(self):
        parser = make_parser()
        curHandler = XmlHandler()
        parser.setContentHandler(curHandler)
        f = open(self.restoreMetaFile)
        parser.parse(f)
        f.close()
        self.tokenizer = curHandler.get_tokenizer()
        self.token_id = curHandler.get_token_id()

    def get_tokenizer(self):
        return self.tokenizer

    def get_token_id(self):
        return self.token_id

def main(filepath):
    # Initialize the variable
    annotation_tree = annotationtree.AnnotationTree(data.GRAID)

    # Open the raw file
    basename = filepath.split('.pickle')
    file = os.path.abspath(basename[0] + '.txt')
    f_raw = codecs.open(file, 'r', 'utf-8')

    # Getting the raw content
    content = f_raw.readlines()

    # This tree i'll contain the elements to
    # the pickle file
    tree = []

    # Getting the words
    procContent = ProcessContent(basename[0] + '-word.xml')
    procContent.process()
    word_range = procContent.get_tokenizer()
    word_ids = procContent.get_token_id()

    # Getting the clause units
    procContent = ProcessContent(basename[0] + '-clause.xml')
    procContent.process()
    clause_range = procContent.get_tokenizer()
    clause_ids = procContent.get_token_id()

    # Getting the wfw
    wfw_values = []
    xmldoc = minidom.parse(basename[0] + '-wfw.xml')

    procContent = ProcessContent(basename[0] + '-wfw.xml')
    procContent.process()
    wfw_link = procContent.get_tokenizer()
    i = 0

    for node in xmldoc.getElementsByTagName('f'):
        wfw_range = (node.firstChild.nodeValue, wfw_link[i])
        wfw_values.append(wfw_range)
        i+=1

    # Getting the graid1
    graid1_values = []
    xmldoc = minidom.parse(basename[0] + '-graid1.xml')

    procContent = ProcessContent(basename[0] + '-graid1.xml')
    procContent.process()
    graid1_link = procContent.get_tokenizer()
    i = 0

    for node in xmldoc.getElementsByTagName('f'):
        graid1_range = (node.firstChild.nodeValue, graid1_link[i])
        graid1_values.append(graid1_range)
        i+=1

    # Getting the graid2
    graid2_values = []
    xmldoc = minidom.parse(basename[0] + '-graid2.xml')

    procContent = ProcessContent(basename[0] + '-graid2.xml')
    procContent.process()
    graid2_link = procContent.get_tokenizer()
    i = 0

    for node in xmldoc.getElementsByTagName('f'):
        graid2_range = (node.firstChild.nodeValue, graid2_link[i])
        graid2_values.append(graid2_range)
        i+=1

    # Getting the translations
    trans_values = []
    xmldoc = minidom.parse(basename[0] + '-trans.xml')

    procContent = ProcessContent(basename[0] + '-trans.xml')
    procContent.process()
    trans_link = procContent.get_tokenizer()
    i = 0

    for node in xmldoc.getElementsByTagName('f'):
        trans_range = (node.firstChild.nodeValue, trans_link[i])
        trans_values.append(trans_range)
        i+=1

    # Getting the comments
    cmts_values = []
    xmldoc = minidom.parse(basename[0] + '-cmt.xml')

    procContent = ProcessContent(basename[0] + '-cmt.xml')
    procContent.process()
    cmts_link = procContent.get_tokenizer()
    i = 0

    for node in xmldoc.getElementsByTagName('f'):
        cmts_range = (node.firstChild.nodeValue, cmts_link[i])
        cmts_values.append(cmts_range)
        i+=1

    for i, line in enumerate(content):

        # Initialize the variables
        il_elements = list()
        il_clauses = list()
        words = []
        clause_units = []
        wfws = []
        graid1s = []
        graid2s = []

        last_pos = 0

        # Getting the utterance
        utterance = line.rstrip('\n')
        i+=1

        # Anchors in the regions
        # Parse the words from which line
        while last_pos <= int(len(utterance)):
            try:
                w = word_range[0]
                id = word_ids[0]
            except:
                break

            first_pos = last_pos
            last_pos = abs(int(w[1]) - int(w[0]) + first_pos + 1)
            words.append(utterance[first_pos:last_pos])

            for wfw_v in wfw_values:
                if wfw_v[1] == id:
                    wfws.append(wfw_v[0])
                    break

            for graid1_v in graid1_values:
                if graid1_v[1] == id:
                    graid1s.append(graid1_v[0])
                    break

            # Remove the word of the range to not look
            # for it again
            if last_pos <= int(len(line)):
                try:
                    del word_range[0]
                    del word_ids[0]
                except:
                    break

        for w in words:
            if w == '':
                continue

            try:
                wfw = wfws[0]
            except:
                wfw = ''

            try:
                graid1 = graid1s[0]
            except:
                graid1 = ''

            il_elements.append([
                    { 'id' : annotation_tree.next_annotation_id,
                      'annotation' :  w },
                    { 'id' : annotation_tree.next_annotation_id,
                      'annotation' : wfw },
                    { 'id' : annotation_tree.next_annotation_id,
                      'annotation' : graid1 }])

            if not wfw == '':
                del wfws[0]

            if not graid1 == '':
                del graid1s[0]

        # Reset the last position
        last_pos = 0

        # Anchors in the regions
        # Parse the clause units from which line
        while last_pos < int(len(utterance)):
            try:
                c = clause_range[0]
                id = clause_ids[0]
            except:
                break

            first_pos = last_pos
            last_pos = abs(int(c[1]) - int(c[0]) + first_pos)
            st = utterance[first_pos:last_pos]
            clause_units.append(st)

            for graid2_v in graid2_values:
                if graid2_v[1] == id:
                    graid2s.append(str(graid2_v[0]))
                    break

            # Remove the word of the range to not look
            # for it again
            if last_pos <= int(len(line)):
                try:
                    del clause_range[0]
                    del clause_ids[0]
                except:
                    break

        aux_count = 0

        for clause in clause_units:
            try:
                graid2 = graid2s[0]
            except:
                graid2 = ''

            if(aux_count == 0):
                il_clauses.append([{
                         'id' : annotation_tree.next_annotation_id,
                          'annotation' :  clause},
                    il_elements,
                        { 'id' : annotation_tree.next_annotation_id,
                          'annotation' : graid2 }])
            else:
                il_elements = list()
                il_elements.append([
                        { 'id' : annotation_tree.next_annotation_id,
                          'annotation' :  '' },
                        { 'id' : annotation_tree.next_annotation_id,
                          'annotation' : '' },
                        { 'id' : annotation_tree.next_annotation_id,
                          'annotation' : '' }])

                il_clauses.append([{
                    'id' : annotation_tree.next_annotation_id,
                    'annotation' :  clause},
                    il_elements,
                        { 'id' : annotation_tree.next_annotation_id,
                          'annotation' : graid2 }])

            aux_count+=1

            if not graid2 == '':
                del graid2s[0]

        translation = ''
        for trans_v in trans_values:
            if int(trans_v[1]) == (i - 1):
                translation = trans_v[0]
                break
            else:
                translation = ''

        comment = ''
        for cmts_v in cmts_values:
            if int(cmts_v[1]) == (i - 1):
                comment = cmts_v[0]
                break
            else:
                comment = ''

        utterance = [ { 'id' : annotation_tree.next_annotation_id,
                        'annotation' : utterance },
            il_clauses,
                { 'id' : annotation_tree.next_annotation_id,
                  'annotation' : translation },
                { 'id' : annotation_tree.next_annotation_id,
                  'annotation' : comment } ]

        annotation_tree.append_element(utterance)

        tree.append(utterance)

    # Close XML file
    f_raw.close()

    # Create the pickle file
    file = os.path.abspath('/home/alopes/tests/pick.pickle')
    f_pickle = open(file,'wb')
    pickle.dump(tree, f_pickle)
    f_pickle.close()