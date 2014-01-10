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
re_tier_marker = re.compile("^" + r"\\(\S+)(?=($|\s+))", re.UNICODE)
re_line_break = re.compile(r"(\r\n|\n|\r)+$")
re_word = re.compile(r"(?<=\s)(\S+)(?:\s|$)", re.UNICODE)
BOMLEN = len(codecs.BOM_UTF8)

# Set the type of string
if sys.version_info[:2] >= (3, 0):
    string_type = str
else:
    string_type = basestring

def char_len(string):
    """
    Method to calculate string length for Toolbox alignment.
    Based on Taras Zakharko's method.

    """
    return(len(string.encode("utf-8")))

class Parser(poioapi.io.graf.BaseParser):

    def __init__(self, input_stream, record_marker = 'ref',
        record_level_markers = ['ref', 'ft', 'nt', 'rf', 'rt', 'id', 'dt', 'f'],
        word_level_markers = ['tx', 't'],
        morpheme_level_markers = ['mb', 'm'],
        tag_level_markers = ['ge', 'ps', 'g', 'p']):
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
        self._content = list()
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
            new_tier_hierarchy.append([ 'utterance_gen', word_tiers ])

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

        current_record_id = 0
        current_utterance_id = 0
        current_id = 1

        first_marker_found = False
        tier_marker = None

        current_utterance = ""

        # Go through lines in the input file
        for line_number, line in enumerate(self.input_stream):
            # remove BOM
            if line_number == 0:
                if line.startswith(codecs.BOM_UTF8):
                    line = line[BOMLEN:]
            line = line.decode("utf-8", 'ignore')
            line = line.strip()
            if line == "":
                if len(elements) > 0:
                    self._process_record(elements, ids, current_utterance_id)
                    elements = dict()
                    ids = dict()
                continue

            # parse line
            last_tier_marker = tier_marker
            tier_marker = None
            line_content = None
            match_tier_marker = re_tier_marker.search(line)
            if match_tier_marker:
                tier_marker = match_tier_marker.group(1)
                line_content = re_tier_marker.sub("", line)
                line_content = line_content.lstrip()
            else:
                # append to last annotation´s content
                self._annotations_for_parent[
                    ("a{0}".format(current_record_id),
                        last_tier_marker)][-1].value += " " + \
                        line
                tier_marker = last_tier_marker
                continue

            # skip all lines before first record marker
            if not first_marker_found:
                if tier_marker != self.record_marker:
                    continue
                else:
                    first_marker_found = True

            if tier_marker in self.word_level_markers:
                current_utterance += re.sub("\s+", " ", line_content) + " "

            if tier_marker in self.word_level_markers or \
                    tier_marker in self.morpheme_level_markers or \
                    tier_marker in self.tag_level_markers:

                if tier_marker not in elements:
                    elements[tier_marker] = dict()
                if tier_marker not in ids:
                    ids[tier_marker] = dict()

                for j, match in enumerate(re_word.finditer(line)):
                    pos = char_len(line[:match.start(1)])
                    elements[tier_marker][pos] = match.group(1)
                    ids[tier_marker][pos] = "a{0}".format(current_id)
                    current_id += 1

            elif tier_marker in self.record_level_markers:

                if current_utterance != "":
                    current_utterance = current_utterance.rstrip()
                    self._annotations_for_parent[
                        ("a{0}".format(current_record_id),
                            "utterance_gen")].append(poioapi.io.graf.Annotation(
                                "a{0}".format(
                                    current_utterance_id), current_utterance))
                    current_utterance = ""
                    current_utterance_id = current_id
                    current_id += 1

                if tier_marker == self.record_marker:
                    self._annotations_for_parent[
                        (None, tier_marker)].append(
                            poioapi.io.graf.Annotation(
                                "a{0}".format(current_id), line_content))
                    current_record_id = current_id
                else:
                    self._annotations_for_parent[
                        ("a{0}".format(current_record_id), tier_marker)].append(
                            poioapi.io.graf.Annotation(
                                "a{0}".format(current_id), line_content))

                current_id += 1

        self.input_stream.seek(0)
        
    def _process_record(self, elements, ids, utterance_id):
        for tier in self.word_level_markers:

            if not tier in elements:
                continue

            for start_pos in sorted(elements[tier].keys()):
                self._annotations_for_parent[("a{0}".format(
                    utterance_id), tier)].append(poioapi.io.graf.Annotation(
                        ids[tier][start_pos],
                        elements[tier][start_pos]))

        for tier in self.morpheme_level_markers:

            if not tier in elements:
                continue

            parent_tiers = [
                t for t in self.word_level_markers if t in self._tiers]
            assert len(parent_tiers) == 1
            parent_tier = parent_tiers[0]

            for start_pos in sorted(elements[tier].keys()):
                parent_id = None
                for parent_start_pos in sorted(
                        elements[parent_tier].keys()):
                    if parent_start_pos <= start_pos:
                        parent_id = ids[parent_tier][parent_start_pos]

                assert parent_id != None

                self._annotations_for_parent[(parent_id, tier)].append(
                    poioapi.io.graf.Annotation(
                        ids[tier][start_pos],
                        elements[tier][start_pos]))

        for tier in self.tag_level_markers:

            if not tier in elements:
                continue

            parent_tiers = [
                t for t in self.morpheme_level_markers if t in self._tiers]
            assert len(parent_tiers) == 1
            parent_tier = parent_tiers[0]

            for start_pos in sorted(elements[tier].keys()):
                parent_id = None
                for parent_start_pos in sorted(
                        elements[parent_tier].keys()):
                    if parent_start_pos <= start_pos:
                        parent_id = ids[parent_tier][parent_start_pos]

                assert parent_id != None

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
