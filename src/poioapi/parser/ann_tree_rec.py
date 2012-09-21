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
from poioapi import annotationtree
from poioapi import data
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

import pickle
import os

class XmlHandler(ContentHandler):

    def __init__(self):
        self.tokenizer = []
        self.regions = []

    def startElement(self, name, attrs):
        if name == 'region':
            #id = attrs.getValue('xml:id')
            att = attrs.getValue('anchors')
            tokenizer = att.split()
            self.tokenizer.append(tokenizer)

    def characters (self, ch):
        return

    def endElement(self, name):
        return

    def get_tokenizer(self):
        return self.tokenizer

class ProcessContent:

    def __init__(self, restoreMetaFile):
        self.tokenizer = []
        self.restoreMetaFile = restoreMetaFile

    def process(self):
        parser = make_parser()
        curHandler = XmlHandler()
        parser.setContentHandler(curHandler)
        f = open(self.restoreMetaFile)
        parser.parse(f)
        f.close()
        self.tokenizer = curHandler.get_tokenizer()

    def get_tokenizer(self):
        return self.tokenizer

def main():
    # Initialize the variable
    annotation_tree = annotationtree.AnnotationTree(data.GRAID)

    # Open the raw file
    file = os.path.abspath('/home/alopes/tests/raw.txt')
    f_raw = open(file, 'r')

    # Getting the raw content
    content = f_raw.readlines()

    # This tree i'll contain the elements to
    # the pickle file
    tree = []

    # Getting the words
    procContent = ProcessContent('/home/alopes/tests/seg-words.xml')
    procContent.process()
    word_range = procContent.get_tokenizer()

    # Getting the clause units
    procContent = ProcessContent('/home/alopes/tests/seg-clause.xml')
    procContent.process()
    clause_range = procContent.get_tokenizer()

    # Getting the wfw
    procContent = ProcessContent('/home/alopes/tests/seg-wfw.xml')
    procContent.process()
    wfw_range = procContent.get_tokenizer()

    for i, line in enumerate(content):

        # Initialize the variables
        il_elements = list()
        il_clauses = list()
        words = []
        clause_units = []
        last_pos = -1

        # Getting the utterance
        utterance = line.rstrip('\n')

        # Anchors in the regions
        # Parse the words from which line
        while last_pos < int(len(utterance)):
            try:
                w = word_range[0]
            except:
                break
            first_pos = last_pos + 1
            last_pos = abs(int(w[1]) - int(w[0]) + first_pos)
            words.append(utterance[first_pos:last_pos])

            # Remove the word of the range to not look
            # for it again
            if last_pos <= int(len(line)):
                try:
                    del word_range[0]
                except:
                    break

        for w in words:
            il_elements.append([
                    { 'id' : annotation_tree.next_annotation_id,
                      'annotation' :  w },
                    { 'id' : annotation_tree.next_annotation_id,
                      'annotation' : '' },
                    { 'id' : annotation_tree.next_annotation_id,
                      'annotation' : '' }])

        # Reset the last position
        last_pos = -1

        # Anchors in the regions
        # Parse the clause units from which line
        while last_pos < int(len(utterance)):
            try:
                c = clause_range[0]
            except:
                break
            first_pos = last_pos + 1
            last_pos = abs(int(c[1]) - int(c[0]) + first_pos)
            st = str(utterance[first_pos:last_pos])
            clause_units.append(st)

            # Remove the word of the range to not look
            # for it again
            if last_pos <= int(len(line)):
                try:
                    del clause_range[0]
                except:
                    break

        for clause in clause_units:
            il_clauses.append([{
                     'id' : annotation_tree.next_annotation_id,
                      'annotation' :  str(clause)},
                il_elements,
                    { 'id' : annotation_tree.next_annotation_id,
                      'annotation' : 'GRAID2' }])
        #elements = [ [
            #,
            #il_elements,
                #{ 'id' : annotation_tree.next_annotation_id,
                  #'annotation' : 'GRAID2' }] ]

        utterance = [ { 'id' : annotation_tree.next_annotation_id,
                        'annotation' : utterance },
            il_clauses,
                { 'id' : annotation_tree.next_annotation_id,
                  'annotation' : 'TRANSLATION' },
                { 'id' : annotation_tree.next_annotation_id,
                  'annotation' : 'COMMENT' } ]

        annotation_tree.append_element(utterance)

        tree.append(utterance)


    # Close XML file
    f_raw.close()

    # Create the pickle file
    file = os.path.abspath('/home/alopes/tests/pick.pickle')
    f_pickle = open(file,'wb')
    pickle.dump(tree, f_pickle)
    f_pickle.close()