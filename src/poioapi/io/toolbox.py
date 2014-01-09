# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

from __future__ import unicode_literals

import sys
import unicodedata
import re
import codecs
import collections

import poioapi.io.graf
import poioapi.data

# Compile necessary regular expression
re_tier_marker = re.compile("^" + r"\\(\S+)(?=($|\s+))")
re_line_break = re.compile(r"(\r\n|\n|\r)+$")
re_word = re.compile(r"(?<=\s)(\S+)(?:\s|$)", re.UNICODE)

# Set the type of string
if sys.version_info[:2] >= (3, 0):
    string_type = str
else:
    string_type = basestring

class Parser(poioapi.io.graf.BaseParser):

    def __init__(self, input_stream, record_marker = 'ref',
        record_level_markers = ['ref', 'ft', 'nt', 'rf', 'rt', 'id', 'dt'],
        word_level_markers = ['tx'],
        morpheme_level_markers = ['mb'],
        tag_level_markers = ['ge', 'ps']):
        """Class's constructor.

        Parameters
        ----------
        input_stream : str or IO stream
            Path of the Toolbox TXT file.
        record_marker : str
            The marker that marks the start of a Toolbox record in the input
            file.

        """

        self._input_stream = None
        self.tier_hierarchy = None

        self.input_stream = input_stream
        self.record_marker = record_marker

        self.record_level_markers = record_level_markers
        self.word_level_markers = word_level_markers
        self.morpheme_level_markers = morpheme_level_markers
        self.tag_level_markers = tag_level_markers

        self.parse()

    def input_stream():
        doc = "The input_stream property."
        def fget(self):
            return self._input_stream
        def fset(self, value):
            if not hasattr(value, 'read'):
                self._input_stream = open(value, "rb")
            else:
                self._input_stream = value
        def fdel(self):
            del self._input_stream
        return locals()
    input_stream = property(**input_stream())

    def parse(self):
        """This method will parse the input file.

        """
        self._tiers = list()
        self._annotations_for_parent = collections.defaultdict(list)
        self._get_tiers()

        # create tier hierarchy
        if self.tier_hierarchy == None:
            new_tier_hierarchy = [ self.record_marker ]
            
            word_tiers = [
                t for t in self.word_level_markers if t in self._tiers]
            morpheme_tiers = [
                t for t in self.morpheme_level_markers if t in self._tiers]
            tag_tiers = [
                t for t in self.tag_level_markers if t in self._tiers]
            morpheme_tiers.append(tag_tiers)
            word_tiers.append(morpheme_tiers)
            new_tier_hierarchy.append(word_tiers)

            record_tiers = [t for t in self.record_level_markers \
                if t in self._tiers and t != self.record_marker]
            new_tier_hierarchy.append(record_tiers)

            self.tier_hierarchy = poioapi.data.DataStructureType(
                new_tier_hierarchy)
        
        self._build_annotations()

    def _get_tiers(self):
        # Go through lines in the input file
        for line in self.input_stream:
            # Hack: sometimes there are characters that we cannot decode
            line = line.decode("utf-8", 'ignore')
            match_tier_marker = re_tier_marker.search(line)
            if match_tier_marker:
                tier_marker = match_tier_marker.group(1)
            if tier_marker not in self._tiers:
                self._tiers.append(tier_marker)
        self.input_stream.seek(0)

    def _build_annotations(self):
        """
        Helper method to parse the input file and store intermediate information
        in attributes.

        """
 
        elements = dict()
        ids = dict()
        current_id = 0

        first_marker_found = False
       
        # Go through lines in the input file
        for line in self.input_stream:
            # Hack: sometimes there are characters that we cannot decode
            line = line.decode("utf-8", 'ignore')
            line = line.strip()
            if line == "":
                continue

            tier_marker = None
            match_tier_marker = re_tier_marker.search(line)
            if match_tier_marker:
                tier_marker = match_tier_marker.group(1)
            else:
                continue

            if not first_marker_found:
                if tier_marker != self.record_marker:
                    continue
                else:
                    first_marker_found = True

            if tier_marker == self.record_marker:
                if len(elements) > 0:
                    self._process_record(elements, ids)
                    elements = dict()
                    ids = dict()

            if tier_marker not in elements:
                elements[tier_marker] = dict()
            if tier_marker not in ids:
                ids[tier_marker] = dict()

            if tier_marker in self.word_level_markers or \
                    tier_marker in self.morpheme_level_markers or \
                    tier_marker in self.tag_level_markers:
                for j, match in enumerate(re_word.finditer(line)):
                    elements[tier_marker][match.start(1)] = match.group(1)
                    ids[tier_marker][match.start(1)] = "a{0}".format(current_id)
                    current_id += 1
            else:
                content = re_tier_marker.sub("", line)
                elements[tier_marker][len(match_tier_marker.group(0))] = content
                ids[tier_marker][len(match_tier_marker.group(0))] = \
                    "a{0}".format(current_id)
                current_id += 1


        # process last record
        if len(elements) > 0:
            self._process_record(elements, ids)

        self.input_stream.seek(0)
        
    def _process_record(self, elements, ids):
        for tier in self.tier_hierarchy.flat_data_hierarchy:
            parent_tiers = [t for t in self.tier_hierarchy.get_parents_of_type(
                tier) if t in self._tiers]

            if not tier in elements:
                continue

            for start_pos in sorted(elements[tier].keys()):
                parent_id = None

                for parent_tier in parent_tiers:
                    for parent_start_pos in sorted(
                            elements[parent_tier].keys()):
                        if parent_start_pos <= start_pos:
                            parent_id = ids[parent_tier][parent_start_pos]

                self._annotations_for_parent[(parent_id, tier)].append(
                    poioapi.io.graf.Annotation(
                        ids[tier][start_pos],
                        elements[tier][start_pos]))

    def get_root_tiers(self):
        return [poioapi.io.graf.Tier(self.record_marker)]

    def get_child_tiers_for_tier(self, tier):
        return [poioapi.io.graf.Tier(t) \
            for t in self.tier_hierarchy.get_children_of_type(tier.name)]

    def get_annotations_for_tier(self, tier, annotation_parent=None):
        parent_id = None
        if annotation_parent:
            parent_id = annotation_parent.id
        return self._annotations_for_parent[(parent_id, tier.name)]

    def tier_has_regions(self, tier):
        return False

    def region_for_annotation(self, annotation):
        return None


    def get_primary_data(self):
        """This method returns the primary data of the Toolbox file.

        Returns
        -------
        primary_data : object
            PrimaryData object.

        """

        primary_data = poioapi.io.graf.PrimaryData()
        primary_data.type = poioapi.io.graf.NONE
        primary_data.filename = "unknown"

        return primary_data
