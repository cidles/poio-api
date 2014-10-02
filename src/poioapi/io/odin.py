# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: Peter Bouda <pbouda@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT
import re
import xml.etree.ElementTree as ET
import codecs
import collections
import unicodedata

import poioapi.io.graf
import poioapi.data
import poioapi.mapper


def tier_mapping():
    mapping = poioapi.mapper.TierMapper()
    mapping.append_to_tier_labels(poioapi.data.TIER_UTTERANCE, ['phrase'])
    mapping.append_to_tier_labels(poioapi.data.TIER_WORD, ['word'])
    mapping.append_to_tier_labels(poioapi.data.TIER_TRANSLATION, ['translation'])
    mapping.append_to_tier_labels(poioapi.data.TIER_MORPHEME, ['morpheme'])
    mapping.append_to_tier_labels(poioapi.data.TIER_GLOSS, ['gloss'])
    mapping.append_to_tier_labels(poioapi.data.TIER_POS, ['pos'])

    return mapping


class MalformedOdin(Exception):
    pass


class Parser(poioapi.io.graf.BaseParser):

    def __init__(self, input_stream, tier_label_map=None):
        """Class's constructor.

        Parameters
        ----------
        :param input_stream: str or IOBase
            Path of the ODIN source file.
        :param tier_label_map: the tier mapping for the file

        """

        # regular expression to detect ignorable parts at the END of the <line> element.
        self._author_detection = [
            r'\w* \d+[: ]+\d+',  # for lines ending with one name author
            r'\w+[; ]+\w+ \d+[: ]+\d+',  # for lines ending with two name author
        ]

        self._translation_delims=[
            '\'',
            '`'
        ]

        #initializing ids
        self._current_ids = dict()
        self._init_current_ids()

        self._tier_block = dict()
        self._init_tier_block()

        if tier_label_map is None:
            self._tier_labels = tier_mapping()
        else:
            self._tier_labels = tier_label_map

        self._annotations_for_parent = collections.defaultdict(list)

        # metadata storage
        self.metadata = dict()
        self._record_tag = 'source'
        self._full_lang = None

        self._tier_hierarchy = None

        self.parse(input_stream)

    def tier_labels():
        doc = "The tier_labels property."

        def fget(self):
            return self._tier_labels

        def fset(self, value):
            if type(value) is poioapi.mapper.TierMapper:
                self._tier_labels = value

        def fdel(self):
            del self._tier_labels
        return locals()
    tier_labels = property(**tier_labels())

    def parse(self, inputfile):
        """ Main parsing function for ODIN files.

        Parameter
        ---------
        :param inputfile: str
            The path of the source file

        """
        #parse the xml file
        root = ET.parse(inputfile)

        # storing the language in the metadata dictionary
        language = root.getroot()
        self.metadata['lang'] = language.get('code', default='und')
        self._full_lang = language.get('name', default=None)

        sources = root.findall('sources/source')
        for source in sources:
            self._source_count += 1

            # incrementing record record_id
            self._current_ids['record'] = self._current_ids['seq']
            self._current_ids['seq'] += 1

            # build the metadata for the current record
            record_metadata = self._build_source_metadata(source)
            record_id = 'a{0}'.format(self._current_ids['record'])
            # annotate source element (acts as record level)
            self._annotations_for_parent[(None, self._record_tag)].append(
                poioapi.io.graf.Annotation(record_id, ''))

            self.metadata[record_id] = record_metadata

            # each source element only has a single igt element. so it should
            # be safe to do this
            examples = source.findall('igt/example')
            for example in examples:
                if self._build_tier_block(example):
                    self._phrase_count += 1  # debug
                    self._handle_example_element(record_id)
                    self._init_tier_block()

    def _build_tier_block(self, element):
        """ Function to build a tier block for processing. Also does cleaning
            of the data.

        Parameters
        ----------
        :param element: xml.etree.ElementTree.Element
            An 'example' element that contains the IGT data.

        Return
        ------
        :return: boolean
            True if the element given contains a valid tier block.
        """
        lines = element.findall('line')
        for line_number, line in enumerate(lines):
            if line_number == 0:  # first line - phrase, word and morphemes
                text = line.text
                if text.find('/') != -1:
                    return False
                text = self._sanitize_line(text, False)
                # phrase = text.replace('-', '')
                # phrase = self._sanitize_line(phrase, True)
                self._tier_block['phrase'] = text
                self._tier_block['word'] = text
                self._tier_block['morpheme'] = text

            elif line_number == 1:  # second line - gloss and pos
                text = self._sanitize_line(line.text, False)
                self._tier_block['gloss'] = text
            elif line_number == 2:  # third line - translation
                text = self._clean_translation_line(line.text)
                self._tier_block['translation'] = text

        return True

    def _build_source_metadata(self, source_element):
        """ Method that extracts the relevant metadata from each 'source'
            (text) of the input file.

        Parameter
        ---------
        :param source_element: xml.etree.ElementTree.Element
            A 'source' element of the file.
        """
        url_element = source_element.find('url')
        odin_url_element = source_element.find('odin')
        citation_element = source_element.find('citation')

        metadata = dict()

        if url_element is not None:
            metadata['source_link'] = url_element.text
        # else:
        #     msg = 'No url present:\n' + ET.tostring(source_element)
        #     print('----- PARSING ERROR -----')
        #     print(msg)
        #     print('-------------------------')

        if odin_url_element is not None:
            metadata['source_archive_link'] = odin_url_element.text
        # else:
        #     msg = 'No odin url present:\n' + ET.tostring(source_element)
        #     print('----- PARSING ERROR -----')
        #     print(msg)
        #     print('-------------------------')

        if citation_element is not None:
            metadata['source_description'] = url_element.text
        # else:
        #     msg = 'No citation present:\n' + ET.tostring(source_element)
        #     print('----- PARSING ERROR -----')
        #     print(msg)
        #     print('-------------------------')

        return metadata

    def _handle_example_element(self, record_id):
        """ Annotates a tier block that was previously built with
            _build_tier_block

        Parameter
        ---------
        :param record_id: str
            The text id to which the tier block belongs.
        """
        #annotate phrase
        self._current_ids['phrase'] = self._current_ids['seq']
        self._current_ids['seq'] += 1
        ann_type = self._tier_labels.tier_label(poioapi.data.TIER_UTTERANCE)
        phrase_id = 'a{0}'.format(self._current_ids['phrase'])
        self._annotations_for_parent[(record_id, ann_type)].append(
            poioapi.io.graf.Annotation(phrase_id, self._tier_block['phrase']))

        # validate quantities of words/morphemes and glosses
        words = self._tier_block['word'].split()
        morphemes = self._tier_block['morpheme'].split()
        glosses = self._tier_block['gloss'].split()
        gt_with_underscore = [a for a in glosses
                              if self._string_has_char_inside(a, '_')]

        if len(morphemes) > len(glosses):
            if len(gt_with_underscore) == 0:
                return

        # annotate the rest.
        gloss_to_next_word = None
        gloss_idx = 0
        for word, morpheme in zip(words, morphemes):
            # words
            self._current_ids['word'] = self._current_ids['seq']
            self._current_ids['seq'] += 1
            word_id = 'a{0}'.format(self._current_ids['word'])
            word_type = self._tier_labels.tier_label(poioapi.data.TIER_WORD)
            self._annotations_for_parent[(phrase_id, word_type)].append(
                poioapi.io.graf.Annotation(word_id, word))

            # morphemes and glosses
            if self._string_has_char_inside(morpheme, '-'):
                morphemes_for_word = morpheme.split('-')
                # assuming that if the morpheme has hyphen, so does the gloss
                # and that the gloss special case doesn't occur
                glosses_for_word = glosses[gloss_idx].split('-')
                for m, g in zip(morphemes_for_word, glosses_for_word):
                    # morpheme handling done, annotate it
                    self._annotate_morpheme(m)
                    for sg in g.split('.'):
                        # gloss handling finished, annotate
                        self._annotate_gloss(sg)

                # increment the gloss indexer
                gloss_idx += 1
            else:
                # morpheme handling is done, annotate it
                self._annotate_morpheme(morpheme)
                if gloss_to_next_word is not None:
                    self._annotate_gloss(gloss_to_next_word)
                    gloss_to_next_word = None
                else:
                    gloss = glosses[gloss_idx]
                    if self._string_has_char_inside(gloss, '_'):
                        # assuming that if it has an underscore, it is only one
                        gt = gloss.split('_')
                        self._annotate_gloss(gt[0])
                        gloss_to_next_word = gt[1]
                    else:
                        self._annotate_gloss(gloss)
                        gloss_to_next_word = None
                    # increment the gloss indexer
                    gloss_idx += 1
        self._annotate_translation(phrase_id)

    def _annotate_translation(self, phrase_id):
        """ Annotates a translation.

        Parameter
        ---------
        :param phrase_id: str
            The id of the phrase that the translation belongs to.

        """

        self._current_ids['translation'] = self._current_ids['seq']
        self._current_ids['seq'] += 1
        tr_id = 'a{0}'.format(self._current_ids['translation'])
        tr_type = self._tier_labels.tier_label(poioapi.data.TIER_TRANSLATION)
        self._annotations_for_parent[(phrase_id, tr_type)].append(
            poioapi.io.graf.Annotation(tr_id, self._tier_block['translation']))

    def _annotate_morpheme(self, m):
        """ Annotates a morpheme

        Parameter
        ---------
        :param m: str
            The annotation value of the morpheme to annotate.
        """
        self._current_ids['morpheme'] = self._current_ids['seq']
        self._current_ids['seq'] += 1
        word_id = 'a{0}'.format(self._current_ids['word'])
        m_id = 'a{0}'.format(self._current_ids['morpheme'])
        m_type = self._tier_labels.tier_label(poioapi.data.TIER_MORPHEME)
        self._annotations_for_parent[(word_id, m_type)].append(
            poioapi.io.graf.Annotation(m_id, m))

    def _annotate_gloss(self, g):
        """ Annotates a gloss

        Parameter
        ---------
        :param g: str
            The annotation value of the gloss to annotate.
        """
        self._current_ids['gloss'] = self._current_ids['seq']
        self._current_ids['seq'] += 1
        m_id = 'a{0}'.format(self._current_ids['morpheme'])
        g_id = 'a{0}'.format(self._current_ids['gloss'])
        g_type = self._tier_labels.tier_label(poioapi.data.TIER_GLOSS)
        self._annotations_for_parent[(m_id, g_type)].append(
            poioapi.io.graf.Annotation(g_id, g))

    def _string_has_char_inside(self, string, char):
        """ Function to check if a char is inside a string, but not in its edges.

        Parameters
        ----------
        :param string: str
            The string to be checked.
        :param char: str
            The char to check for.

        Return
        ------
        :return: boolean
            True if the char if the char is found and is not at the edges of
            the string.
        """
        idx = string.find(char)
        return idx != -1 and idx != 0 and idx != len(string) - 1

    def _clean_translation_line(self, line):
        """ Function to perform specific cleaning of the translation tier.

        Parameter
        ---------
        :param line:
            The line to be cleaned.
        Return
        ------
        :return: str
            The parameter, after cleaning.
        """
        line = line.strip()
        for delim in self._translation_delims:
            line = line.strip(delim)

        return line

    def _sanitize_line(self, line, phrase=True):
        """ Function to clean a tier.

        Parameters
        ----------
        :param line: str
            The line to clean.
        :param phrase: boolean
            Indicates if the tier to be sanitized is a phrase tier. This tier
            has needs for specific cleaning.

        Return
        ------
        :return:
        """
        author_at_end = '[\[\(](?:'
        author_at_end += '|'.join(self._author_detection)
        author_at_end += ')[\)\]](?=$)'

        if phrase:
            re.sub(r'\b_+\b', '', line)

        line = re.sub(r'^(?:\(?\d+\))?(?:\s*[a-z]\.)?', '', line)
        line = re.sub(r'^\(?\d+[a-z]+\)', '', line)
        line = re.sub(r'^\d+\.', '', line)
        if self._full_lang is not None and self._full_lang != '':
            line = re.sub(self._full_lang + ':', '', line)
        line = re.sub(author_at_end, '', line)
        line = re.sub(r'(?:DECL|WH|IMP): \w+$', '', line)
        line = re.sub(r'\(?\w*\s*PORTUGUESE\)?$', '', line, flags=re.IGNORECASE)
        line = line.strip('(')
        line = line.strip(')')

        # for now we are not implementing validity, so we clean it
        line = re.sub(r'[*?#]', '', line)

        # possible speaker attribute cleaning. confirm if it is to ignore or not
        line = re.sub(r'^(?:Interviewer|Aphasic):', '', line)

        # if anymore cleaning needs to be done, add it before this line
        line = re.sub(r'\s+', ' ', line)

        sq_brackets = re.search(r'\[.*\]', line)
        if sq_brackets is not None:
            start = sq_brackets.start() + 1
            end = sq_brackets.end() - 1
            inner = line[start:end]
            if len(inner) == 1:
                name = unicodedata.name(inner).lower()
                if name.find('ellipsis') != -1:
                    return line.strip()
            if re.match(r'^[ .]*$', line) is not None:
                return line.strip()
            line = re.sub(r'\[', '', line)
            line = re.sub(r'\]', '', line)

        line = line.strip()

        return line

    def _init_current_ids(self):
        """ Method to initialize the annotation IDs tracking dictionary.
            'seq' counter represents the numeric part of an annotation.
        """
        self._current_ids['seq'] = 0
        self._current_ids['record'] = 0
        self._current_ids['phrase'] = 0
        self._current_ids['word'] = 0
        self._current_ids['morpheme'] = 0
        self._current_ids['gloss'] = 0
        self._current_ids['pos'] = 0
        self._current_ids['translation'] = 0

    def _init_tier_block(self):
        """ Method to initialize the tier block dictionary.
        """
        self._tier_block['phrase'] = ''
        self._tier_block['word'] = ''
        self._tier_block['morpheme'] = ''
        self._tier_block['gloss'] = ''
        self._tier_block['translation'] = ''

    def get_child_tiers_for_tier(self, tier):

        if tier.name == self._record_tag:
            return [poioapi.io.graf.Tier(self._tier_labels.tier_label(poioapi.data.TIER_UTTERANCE))]
        if tier.name in self._tier_labels.tier_labels(poioapi.data.TIER_UTTERANCE):
            return [poioapi.io.graf.Tier(self._tier_labels.tier_label(poioapi.data.TIER_WORD)),
                    poioapi.io.graf.Tier(self._tier_labels.tier_label(poioapi.data.TIER_TRANSLATION))]
        elif tier.name in self._tier_labels.tier_labels(poioapi.data.TIER_WORD):
            return [poioapi.io.graf.Tier(self._tier_labels.tier_label(poioapi.data.TIER_MORPHEME))]
        elif tier.name in self._tier_labels.tier_labels(poioapi.data.TIER_MORPHEME):
            return [poioapi.io.graf.Tier(self._tier_labels.tier_label(poioapi.data.TIER_GLOSS))]

    def get_annotations_for_tier(self, tier, annotation_parent=None):

        parent_id = None
        if annotation_parent:
            parent_id = annotation_parent.id
        return self._annotations_for_parent[(parent_id, tier.name)]

    def region_for_annotation(self, annotation):
        return None

    def get_primary_data(self):
        """This method returns the primary data of the Odin file.

		Returns
		-------
		 :return primary_data : poioapi.io.graf.PrimaryData
			PrimaryData object.

		"""
        primary_data = poioapi.io.graf.PrimaryData()
        primary_data.type = poioapi.io.graf.NONE
        primary_data.filename = "unknown"

        return primary_data

    def tier_has_regions(self, tier):
        return False

    def get_root_tiers(self):
        """This method retrieves all the root tiers.

		Returns
		-------
		:return list : array-like
			List of tiers type.

		"""

        return [poioapi.io.graf.Tier(self._record_tag)]