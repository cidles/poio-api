# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2014 Poio Project
# Author: Peter Bouda <pbouda@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

from __future__ import unicode_literals

import re
import codecs
import collections

import poioapi.io.graf
import poioapi.data
import poioapi.mapper

re_last_quote = re.compile("[^\"]*$")

#helpful in detecting the gloss tier
glosses = ['2SG', '1SG', '3SG', '1PL', '2PL', '3PL', 'ABSTR', 'ACPN', 'ACPP', 'ADVCL', 'ANTIP', 'APPART', 'ASSOC',
              'BEN', 'CAUS', 'CONT', 'CONTR', 'COPID', 'COPLOC', 'COPN', 'CTRP', 'D', 'DEF', 'DEM', 'DEST', 'EMPH',
              'FOC', 'GEN', 'GER', 'HAB', 'INACN', 'INACP', 'INDEF', 'INF', 'INT', 'INTERJ', 'LOC', 'MAN', 'MTV',
              'NMAG', 'NMINS', 'OBL', 'OBLIG', 'OPT', 'ORD', 'ORN', 'PAS', 'PL', 'PLASS', 'POT', 'PREDS', 'PROG',
              'PRIV', 'Q', 'QUOT', 'RECIP', 'REFL', 'REL', 'RES', 'RESID', 'SELECT', 'SPHP', 'SUBJN', 'SUBJP']

#list of regexes to separate the words line. Add items as they are needed, but DON'T add them after the last regex (\S+)
#This is to account for words that are separated but must be considered as one.
word_line_separators = ['Áŋ aŋ', '\S+']

#The regular expressions to use in line sanitation, and the corresponding substitutes
sanitation_tokens = {
    '«\s': '«',
    '\s»': '»',
    '\s\.\.\.': '...',
    '\s!': '!',
    '\s\?': '?',
    '^\W\s': '',
    '[ \t]+': ' '
}

#list of phrase termination detection tokens
phrase_terminators = [
    '[\.!\?]$',
    '[\.!\?]"$',
    '[\.!\?]»$'
]

#list of regexes to identify ignorable lines.
ignore_these = ['^\sMmm...\s',
                '^\smmm...',
                '^Conte\s\d\s',
                '^\d\. Proverbes\s',
                '^\sŊ́ jáŋka, ŋ́ jáŋka, ŋ́ jáŋká saayéwo balléerôo féle !',
                '^\sFíndímúŋkû féle, ŋ́ jáŋká saayéwo balléerôo féle !',
                '^\sMaanimúŋkû féle, ŋ́ jáŋká saayéwo balléerôo féle !',
                '^\[et Fatou à son tour chante\]',
                '^\d\.\sDiscussions\s',
                '^La cuisson du sel',
                'Les trois textes suivants.*',
                '^La prise de pouvoir des Mandingues musulmans dans le Pakao',
                '^Ce récit évoque un épisode',
                '^La condition féminine',
                '^En Casamance \(et en particulier dans les environs de Sédhiou\)',
                '^Ce récit évoque un épisode crucial',
                '\s+\(formule en arabe\)',
                '^«\s+Bisímilláahí ',
                '^[\r\n]']


def tier_mapping():
    mapping = poioapi.mapper.TierMapper()
    mapping.append_to_tier_labels(poioapi.data.TIER_UTTERANCE, ['phrase'])
    mapping.append_to_tier_labels(poioapi.data.TIER_WORD, ['word'])
    mapping.append_to_tier_labels(poioapi.data.TIER_TRANSLATION, ['translation'])
    mapping.append_to_tier_labels(poioapi.data.TIER_MORPHEME, ['morpheme'])
    mapping.append_to_tier_labels(poioapi.data.TIER_GLOSS, ['gloss'])
    mapping.append_to_tier_labels(poioapi.data.TIER_POS, ['pos'])

    return mapping


class Parser(poioapi.io.graf.BaseParser):
    """
    Class that will handle the parsing of Mandinka data.

    """

    def __init__(self, input_stream, tier_label_map):
        """Class's constructor.

        Parameters
        ----------
        stream : str or IOBase
            Path of the Mandinka source file or an IO.stream.

        """
        self._input_stream = None

        if tier_label_map is None:
            self._tier_labels = tier_mapping()
        else:
            self._tier_labels = tier_label_map

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
        current_id = 0
        current_phrase_id = 0
        current_tier_id = 0
        current_word_id = 0
        current_morpheme_id = 0
        current_gloss_id = 0
        current_translation_id = 0
        current_block = 0
        block_line_count = 3
        block = {}
        line_count = 0
        phrase_ended = False

        #compile all regexes structures defined
        separate = re.compile(r'\b(?:%s)\b' % '|'.join(word_line_separators))
        ignore_lines = re.compile('|'.join(ignore_these))
        terminators = re.compile('|'.join(phrase_terminators))

        self._annotations_for_parent = collections.defaultdict(list)

        block['phrase'] = ''
        block['gloss'] = ''
        block['translation'] = ''

        while 1:
            line = self.input_stream.readline()
            if not line:
                break
            #ignoring garbage and blank lines
            if not(ignore_lines.match(line) or len(line) == 0):
                line = self.sanitize_line(line)
                if line_count == 0:
                    block['phrase'] += line
                    #block['phrase'] = 'phrase'
                elif line_count == 1:
                    block['gloss'] += line
                    #block['gloss'] = 'gloss'
                elif line_count == 2:
                    block['translation'] += line
                    #block['translation'] = 'translation'
                line_count += 1
                if line_count == block_line_count:
                    line_count = 0
                    if terminators.search(block['phrase']):
                        phrase_ended = True
                    else:
                        phrase_ended = False
                        block['phrase'] += ' '
                        block['gloss'] += ' '
                        block['translation'] += ' '

                if phrase_ended:
                    #adding the annotations for phrase
                    current_phrase_id = current_id
                    self._annotations_for_parent[(None, self._tier_labels.tier_labels(
                                                                            poioapi.data.TIER_UTTERANCE)[0])].append(
                        poioapi.io.graf.Annotation('a{0}'.format(current_phrase_id),
                                                   re.sub('[-]+', '', block['phrase'])))

                    word_tokens = separate.findall(block['phrase'])

                    #basic space-driven split for the gloss line
                    gloss_tokens = block['gloss'].split(' ')

                    for i in range(0, len(word_tokens), 1):
                        current_id += 1
                        current_word_id = current_id
                        #add the word tier annotations
                        self._annotations_for_parent[('a{0}'.format(current_phrase_id),
                                                      self._tier_labels.tier_labels(poioapi.data.TIER_WORD)[0])].append(
                            poioapi.io.graf.Annotation('a{0}'.format(current_word_id),
                                                       re.sub('[-]+', '', word_tokens[i].strip())))
                        morphemes_for_word = word_tokens[i].split('-')
                        glosses_for_word = gloss_tokens[i].split('-')

                        #add the morphemes and the glosses, reading both lines simultaneously.
                        #Its vital that they have the same number of elements.
                        while len(morphemes_for_word) > 0 and len(glosses_for_word) > 0:
                            morpheme = morphemes_for_word.pop(0)
                            gloss_word = glosses_for_word.pop(0)
                            current_id += 1
                            current_morpheme_id = current_id
                            self._annotations_for_parent[('a{0}'.format(current_word_id),
                                                          self._tier_labels.tier_labels(
                                                              poioapi.data.TIER_MORPHEME)[0])].append(
                                poioapi.io.graf.Annotation('a{0}'.format(current_morpheme_id), morpheme.strip()))

                            #if the morpheme and gloss counts for this word don't match,
                            #join all remaining glosses in the last one.
                            if len(morphemes_for_word) == 0 and len(glosses_for_word) > 0:
                                while len(glosses_for_word) > 0:
                                    gloss_word += '.' + glosses_for_word.pop(0)

                            glosses_for_morpheme = gloss_word.split('.')
                            for gloss in glosses_for_morpheme:
                                current_id += 1
                                current_gloss_id = current_id
                                self._annotations_for_parent[('a{0}'.format(current_morpheme_id),
                                                              self._tier_labels.tier_labels(
                                                                  poioapi.data.TIER_GLOSS)[0])].append(
                                    poioapi.io.graf.Annotation('a{0}'.format(current_gloss_id), gloss.strip()))

                    #finally, add the translation annotation
                    current_id += 1
                    current_translation_id = current_id
                    self._annotations_for_parent[('a{0}'.format(current_phrase_id), self._tier_labels.tier_labels(
                                                                            poioapi.data.TIER_TRANSLATION)[0])].append(
                            poioapi.io.graf.Annotation('a{0}'.format(current_translation_id), block['translation']))

                    #increment the current annotation id for the next phrase
                    current_id += 1
                    current_block += 1
                    phrase_ended = False
                    block['phrase'] = ''
                    block['gloss'] = ''
                    block['translation'] = ''

        # print('Total processed blocks: {0}'.format(current_block))

    def sanitize_line(self, line):
        """ Function to remove unwanted character(s) from the line.
            To define which characters are to be removed, add them to the sanitation_tokens dictionary declared
            in the beginning of the file.

            Parameters
            ----------
            line : string
            The line that is to be sanitized.

            Return
            ------
            line : string
            This is the same as the parameter, but after cleaning.
        """
        for key in sanitation_tokens.keys():
            line = re.sub(key, sanitation_tokens[key], line)
        line = line.strip()
        return line

    def get_root_tiers(self):
        """This method retrieves all the root tiers.

        Returns
        -------
        list : array-like
            List of tiers type.

        """

        return [poioapi.io.graf.Tier(self._tier_labels.tier_labels(poioapi.data.TIER_UTTERANCE)[0])]

    def get_child_tiers_for_tier(self, tier):
        """This method retrieves all the child tiers
        of a specific tier.

        Parameters
        ----------
        tier : poioapi.io.graf.Tier
            Tier to find the children for.

        Returns
        -------
        child_tiers : array-like
            List of tiers type.

        """

        if tier.name == self._tier_labels.tier_labels(poioapi.data.TIER_UTTERANCE)[0]:
            return [poioapi.io.graf.Tier(self._tier_labels.tier_labels(poioapi.data.TIER_WORD)[0]),
                    poioapi.io.graf.Tier(self._tier_labels.tier_labels(poioapi.data.TIER_TRANSLATION)[0])]
        elif tier.name == self._tier_labels.tier_labels(poioapi.data.TIER_WORD)[0]:
            return [poioapi.io.graf.Tier(self._tier_labels.tier_labels(poioapi.data.TIER_MORPHEME)[0])]
        elif tier.name ==self._tier_labels.tier_labels(poioapi.data.TIER_MORPHEME)[0]:
            return [poioapi.io.graf.Tier(self._tier_labels.tier_labels(poioapi.data.TIER_GLOSS)[0])]

    def get_annotations_for_tier(self, tier, annotation_parent=None):
        """This method retrieves all the child tiers
        of a specific tier.

        Parameters
        ----------
        tier : poioapi.io.graf.Tier
            Tier to get the annotations from.
        annoation_parent : poioapi.io.graf.Annotation
            The parent to get the annotations for.

        Returns
        -------
        annotations : list of poioapi.io.graf.Annotation
            List of annotations.

        """
        parent_id = None
        if annotation_parent:
            parent_id = annotation_parent.id
        return self._annotations_for_parent[(parent_id, tier.name)]

    def tier_has_regions(self, tier):
        return False

    def region_for_annotation(self, annotation):
        return None

    def get_primary_data(self):
        """This method returns the primary data of the Mandinka file.

        Returns
        -------
        primary_data : poioapi.io.graf.PrimaryData
            PrimaryData object.

        """
        primary_data = poioapi.io.graf.PrimaryData()
        primary_data.type = poioapi.io.graf.NONE
        primary_data.filename = "unknown"

        return primary_data
