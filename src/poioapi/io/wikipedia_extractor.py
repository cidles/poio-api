# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

from __future__ import absolute_import, unicode_literals

import sys
import os
import codecs

import xml.etree.ElementTree as ET

import poioapi.io.graf

class Parser(poioapi.io.graf.BaseParser):

    def __init__(self, filepath):
        self.filepath = filepath
        (self.basedirname, _) = os.path.splitext(os.path.abspath(self.filepath))

        self.parse()

    def parse(self):
        self.root = ET.parse(self.filepath).getroot()
        self.documents_map = {}
        self.documents = []

    def get_root_tiers(self):
        return [poioapi.io.graf.Tier('doc')]

    def get_child_tiers_for_tier(self, tier):
        pass

    def get_annotations_for_tier(self, tier, annotation_parent=None):
        annotations = []
        last_position = 0

        if tier.name == "doc":
            for a, annotation in enumerate(self.root):
                text = annotation.text
                id = annotation.attrib["id"]

                features = {"title":annotation.attrib["title"],
                            "url":annotation.attrib["url"]}

                annotations.append(poioapi.io.graf.Annotation(id,
                    None, features))

                if len(annotation) is not 0:
                    text += annotation[0].tail

                self.documents_map[id] = (last_position, last_position +
                                                         len(text))
                self.documents.append(text)

                last_position += len(text)

        return annotations

    def region_for_annotation(self, annotation):
        return self.documents_map[annotation.id]

    def tier_has_regions(self, tier):
        if tier.name == 'doc':
            return True

        return False

    def write_raw_file(self):
        file = os.path.abspath(self.basedirname + '.txt')

        if sys.version_info > (2, 7):
            f = codecs.open(file, 'w', 'utf-8')
        else:
            f = open(file, 'w')

        for text in self.documents:
            f.write(text)

        f.close()
