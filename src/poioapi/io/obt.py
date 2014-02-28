# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2014 Poio Project
# Author: Peter Bouda <pbouda@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

import re
import codecs
import collections

import poioapi.io.graf

re_last_quote = re.compile("[^\"]*$")

class Parser(poioapi.io.graf.BaseParser):
    """
    Class that will handle parse of OBT files. OBT is The Oslo-Bergen-Tagger.
    http://www.tekstlab.uio.no/obt-ny/english/index.html

    Code on Github:
    https://github.com/noklesta/The-Oslo-Bergen-Tagger

    """

    def __init__(self, input_stream):
        """Class's constructor.

        Parameters
        ----------
        stream : str or IOBase
            Path of the OBT output file or an IO.stream.

        """
        self._input_stream = None

        self.input_stream = input_stream
        self.parse()

    def input_stream():
        doc = "The input_stream property."
        def fget(self):
            return self._input_stream
        def fset(self, value):
            if not hasattr(value, 'read'):
                self._input_stream = codecs.open(value, "r", "utf-8")
            else:
                self._input_stream = value
        def fdel(self):
            del self._input_stream
        return locals()
    input_stream = property(**input_stream())

    def parse(self):
        """
        This method is called by the constructor. It will parse the input file
        and collect the data in intermediate data structures for later
        processing.

        """
        current_phrase_id = 0
        current_phrase_words = []
        current_id = 1
        current_word_id = None

        self._annotations_for_parent = collections.defaultdict(list)

        for line in self.input_stream:
            line = line.strip()
            if line.startswith("<word>") and line.endswith("</word>"):
                current_word = line[6:-7]
                current_word_id = current_id
                current_id += 1
                # add annotation 
                self._annotations_for_parent[("a{0}".format(current_phrase_id),
                    "word")].append((poioapi.io.graf.Annotation("a{0}".format(
                        current_word_id), 
                        current_word)))
                current_phrase_words.append(current_word)

            elif not line.startswith('"<'):
                last_quote_match = re_last_quote.search(line)
                variant = line[1:last_quote_match.start(0)-1]
                variant_tags = last_quote_match.group(0).split()
                variant_tags = [t for t in variant_tags if t != "<<<" and \
                    t != ">>>"]

                current_variant_id = current_id
                current_id += 1
                self._annotations_for_parent[("a{0}".format(current_word_id),
                    "variant")].append(
                        (poioapi.io.graf.Annotation("a{0}".format(
                            current_variant_id), 
                            variant)))

                for tag in variant_tags:
                    self._annotations_for_parent[("a{0}".format(
                            current_variant_id),
                        "tag")].append(
                            (poioapi.io.graf.Annotation("a{0}".format(
                                current_id), 
                                tag)))
                    current_id += 1

                # create phrase
                if "<punkt>" in variant_tags:
                    current_phrase = " ".join(current_phrase_words)
                    self._annotations_for_parent[(None, "phrase")].append(
                            (poioapi.io.graf.Annotation("a{0}".format(
                                current_phrase_id), 
                                current_phrase)))
                    current_phrase_id = current_id
                    current_id += 1
                    current_phrase_words = []

        # Text might not end with a <punkt>
        if current_phrase_words != []:
            current_phrase = " ".join(current_phrase_words)
            self._annotations_for_parent[(None, "phrase")].append(
                    (poioapi.io.graf.Annotation("a{0}".format(
                        current_phrase_id), 
                        current_phrase)))

    def get_root_tiers(self):
        """This method retrieves all the root tiers.

        Returns
        -------
        list : array-like
            List of tiers type.

        """

        return [poioapi.io.graf.Tier("phrase")]

    def get_child_tiers_for_tier(self, tier):
        """This method retrieves all the child tiers
        of a specific tier.

        Parameters
        ----------
        tier : object
            Tier to find the children from.

        Returns
        -------
        child_tiers : array-like
            List of tiers type.

        """

        if tier.name == "phrase":
            return [poioapi.io.graf.Tier("word")]
        elif tier.name == "word":
            return [poioapi.io.graf.Tier("variant")]
        elif tier.name == "variant":
            return [poioapi.io.graf.Tier("tag")]

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
        """This method returns the primary data of the OBT file.

        Returns
        -------
        primary_data : object
            PrimaryData object.

        """
        primary_data = poioapi.io.graf.PrimaryData()
        primary_data.type = poioapi.io.graf.NONE
        primary_data.filename = "unknown"

        return primary_data
