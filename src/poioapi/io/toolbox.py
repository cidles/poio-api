# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2014 Poio Project
# Author: Peter Bouda <pbouda@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

from __future__ import unicode_literals

import sys
import unicodedata
import re
import codecs
import collections

import poioapi.io.graf
import poioapi.mapper
import poioapi.data

# Compile necessary regular expression
re_tier_marker = re.compile("^" + r"\\(\S+)(?=($|\s+))", re.UNICODE)
re_line_break = re.compile(r"(\r\n|\n|\r)+$")
re_word = re.compile(r"(?<=\s)(\S+)(?:\s|$)", re.UNICODE)
BOMLEN = len(codecs.BOM_UTF8)

# Tier map
# tier_map = {
#     poioapi.data.TIER_UTTERANCE: ["utterance_gen"],
#     poioapi.data.TIER_WORD: ["tx", "t"],
#     poioapi.data.TIER_MORPHEME: ["mb", "m"],
#     poioapi.data.TIER_POS: ["ps", "p"],
#     poioapi.data.TIER_GLOSS: ["ge", "g"],
#     poioapi.data.TIER_TRANSLATION: ["ft", "f"],
#     poioapi.data.TIER_COMMENT: ["nt"]
# }

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


def tier_mapping():
    mapping = poioapi.mapper.TierMapper()
    mapping.append_to_tier_labels(poioapi.data.TIER_UTTERANCE, ['utterance_gen'])
    mapping.append_to_tier_labels(poioapi.data.TIER_WORD, ['tx', 't'])
    mapping.append_to_tier_labels(poioapi.data.TIER_TRANSLATION, ['ft', 'f'])
    mapping.append_to_tier_labels(poioapi.data.TIER_MORPHEME, ['mb', 'm'])
    mapping.append_to_tier_labels(poioapi.data.TIER_GLOSS, ['ge', 'g'])
    mapping.append_to_tier_labels(poioapi.data.TIER_POS, ['ps', 'p']),
    mapping.append_to_tier_labels(poioapi.data.TIER_COMMENT, ['nt'])

    return mapping


class Parser(poioapi.io.graf.BaseParser):

    def __init__(self, input_stream, record_marker='ref',
        record_level_markers = ['ref', 'id', 'dt', 'ELANBegin', 'ELANEnd',
            'ELANParticipant' ],
        utterance_level_markers=  # tier_map[poioapi.data.TIER_TRANSLATION] + \
            #tier_map[poioapi.data.TIER_COMMENT] + \
            ['rf', 'rt', 'np', 'graid', 'pr'],
        #word_level_markers = tier_map[poioapi.data.TIER_WORD],
        #morpheme_level_markers = tier_map[poioapi.data.TIER_MORPHEME],
        #tag_level_markers = tier_map[poioapi.data.TIER_GLOSS] + \
        #    tier_map[poioapi.data.TIER_POS],
        mapper=None):
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

        if mapper is None:
            self._tier_labels = tier_mapping()
        else:
            self._tier_labels = mapper

        self.record_level_markers = record_level_markers
        self.utterance_level_markers = []
        self.utterance_level_markers.extend(utterance_level_markers)
        self.utterance_level_markers.extend(self._tier_labels.tier_labels(poioapi.data.TIER_TRANSLATION))
        self.utterance_level_markers.extend(self._tier_labels.tier_labels(poioapi.data.TIER_COMMENT))

        self.word_level_markers = []
        self.word_level_markers.extend(self._tier_labels.tier_labels(poioapi.data.TIER_WORD))
        self.morpheme_level_markers = []
        self.morpheme_level_markers.extend(self._tier_labels.tier_labels(poioapi.data.TIER_MORPHEME))
        self.tag_level_markers = []
        self.tag_level_markers.extend(self._tier_labels.tier_labels(poioapi.data.TIER_GLOSS))
        self.tag_level_markers.extend(self._tier_labels.tier_labels(poioapi.data.TIER_POS))

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
            utterance_tiers = [
                t for t in self.utterance_level_markers if t in self._tiers]
            morpheme_tiers.append(tag_tiers)
            word_tiers.append(morpheme_tiers)
            new_tier_hierarchy.append([ 'utterance_gen', word_tiers,
                utterance_tiers ])

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
        current_id = 0

        first_marker_found = False
        tier_marker = None

        current_utterance = None

        # Go through lines in the input file
        for line_number, line in enumerate(self.input_stream):
            # remove BOM
            if line_number == 0:

                if line.startswith(codecs.BOM_UTF8):
                    line = line[BOMLEN:]
                    
            line = line.decode("utf-8", 'ignore')
            line = line.strip()

            if "\name" in line:
                self.meta_information = line.split(None,2)[2]

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
            elif first_marker_found:
                # append to last annotation´s content
                id_to_add = current_record_id
                if last_tier_marker in self.utterance_level_markers:
                    id_to_add = current_utterance_id

                self._annotations_for_parent[
                    ("a{0}".format(id_to_add),
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
                # Is it a new utterance? Then create a new ID.
                if current_utterance is None:
                    current_utterance = ""

                if current_utterance == "":
                    current_utterance_id = current_id
                    current_id += 1

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

            # utterance level markers
            elif tier_marker in self.utterance_level_markers:

                # we left the utterance tiers, so create an utterance
                # annotation based on the content and make it the current
                # utterance
                if current_utterance is not None and current_utterance != "":
                    current_utterance = current_utterance.rstrip()
                    self._annotate_utterance(current_record_id,
                                             current_utterance_id,
                                             current_utterance)

                    current_utterance = ""

                elif current_utterance is None:
                    current_utterance_id = current_id
                    current_id += 1
                    self._annotate_utterance(current_record_id,
                                             current_utterance_id, "")

                    current_utterance = ""

                # add the annotation to the current utterance
                self._annotations_for_parent[
                    ("a{0}".format(current_utterance_id), tier_marker)].append(
                        poioapi.io.graf.Annotation(
                            "a{0}".format(current_id), line_content))
                current_id += 1

            # record level markers
            elif tier_marker in self.record_level_markers:

                if tier_marker == self.record_marker:
                    # this is to ensure that the utterance get annotated even
                    # if there were no other utterance_level_markers to cause
                    # it to be
                    if current_utterance is not None and current_utterance != '':
                        self._annotate_utterance(current_record_id,
                                                 current_utterance_id,
                                                 current_utterance)

                    self._annotations_for_parent[
                        (None, tier_marker)].append(
                            poioapi.io.graf.Annotation(
                                "a{0}".format(current_id), line_content))
                    current_record_id = current_id
                    current_id += 1
                    current_utterance = None

                else:
                    # this is to ensure that the utterance get annotated even
                    # if there were no other utterance_level_markers to cause
                    # it to be
                    if current_utterance is not None and current_utterance != '':
                        self._annotate_utterance(current_record_id,
                                                 current_utterance_id,
                                                 current_utterance)

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
            # assert len(parent_tiers) == 1
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
            # assert len(parent_tiers) == 1
            parent_tier = parent_tiers[0]

            for start_pos in sorted(elements[tier].keys()):
                parent_id = None
                for parent_start_pos in sorted(
                        elements[parent_tier].keys()):
                    if parent_start_pos <= start_pos:
                        parent_id = ids[parent_tier][parent_start_pos]

                # assert parent_id != None

                self._annotations_for_parent[(parent_id, tier)].append(
                    poioapi.io.graf.Annotation(
                        ids[tier][start_pos],
                        elements[tier][start_pos]))

    def _annotate_utterance(self, record_id, utterance_id, text):
        self._annotations_for_parent[("a{0}".format(record_id),
                                      "utterance_gen")].append(
            poioapi.io.graf.Annotation("a{0}".format(utterance_id), text))

        pass

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
