# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: Peter Bouda <pbouda@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
"""
CorpusReader, GlossCorpusReader, PosCorpusReader implement a
part of the corpus reader API described in the Natural
Language Toolkit (NLTK):
http://nltk.googlecode.com/svn/trunk/doc/howto/corpus.html

Deprecated. Replaced by classes in module corpus.
"""

from __future__ import unicode_literals

import os, glob
import re

from poioapi import data

# interlinear types: WORDS means "no interlinear"

class CorpusReader(object):
    """
    The base class for all corpus readers. It provides
    access to all data that contain utterances and words.
    """
    def __init__(self, locale = None, participant = None, utterancetierTypes = None, wordtierTypes = None, translationtierTypes = None):
        self.locale = locale
        self.participant = participant
        self.utterancetierTypes = utterancetierTypes
        self.wordtierTypes = wordtierTypes
        self.translationtierTypes = translationtierTypes
        self.postierTypes = None
        self.morphemetierTypes = None
        self.glosstierTypes = None
        self.interlineartype = WORDS
        self.annotationtrees = []

    def addFile(self, filepath, filetype, locale = None, participant = None, utterancetierTypes = None, wordtierTypes = None, translationtierTypes = None, morphemetierTypes = None, glosstierTypes = None, postierTypes = None):
        annotationFileObject = None
        if filetype == data.EAF:
            annotationFileObject = EafAnnotationFileObject(filepath)
        elif filetype == data.EAFFROMTOOLBOX:
            annotationFileObject = EafFromToolboxAnnotationFileObject(filepath)
        elif filetype == data.TOOLBOX:
            annotationFileObject = ToolboxAnnotationFileObject(filepath)
        if annotationFileObject != None:
            annotationTierHandler = annotationFileObject.create_tier_handler()

            # create the parser
            #if self.interlineartype == GLOSS:
            #  annotationParser = annotationFileObject.create_parser(self.interlineartype)
            #elif self.interlineartype == WORDS:
            #  annotationParser = annotationFileObject.create_parser(self.interlineartype)


            annotationTree = AnnotationTree(filepath, self.interlineartype)

            if filetype == data.EAF:
                # Setting the tier types for the parse
                if utterancetierTypes != None:
                    annotationTierHandler.setUtterancetierType(utterancetierTypes)
                elif self.utterancetierTypes != None:
                    annotationTierHandler.setUtterancetierType(self.utterancetierTypes)
    
                if wordtierTypes != None:
                    annotationTierHandler.setWordtierType(wordtierTypes)
                elif self.wordtierTypes != None:
                    annotationTierHandler.setWordtierType(self.wordtierTypes)
    
                if morphemetierTypes != None:
                    annotationTierHandler.setMorphemetierType(morphemetierTypes)
                elif self.morphemetierTypes != None:
                    annotationTierHandler.setMorphemetierType(self.morphemetierTypes)
    
                if glosstierTypes != None:
                    annotationTierHandler.setGlosstierType(glosstierTypes)
                elif self.glosstierTypes != None:
                    annotationTierHandler.setGlosstierType(self.glosstierTypes)
    
                if postierTypes != None:
                    annotationTierHandler.setPostierType(postierTypes)
                elif self.postierTypes != None:
                    annotationTierHandler.setPostierType(self.postierTypes)
    
                if translationtierTypes != None:
                    annotationTierHandler.setTranslationtierType(translationtierTypes)
                elif self.translationtierTypes != None:
                    annotationTierHandler.setTranslationtierType(self.translationtierTypes)

            annotationTree.parse()
            self.annotationtrees.append([filepath, annotationTree])

    def words(self):
        """
        Returns a list of words from the corpus files.
        """
        words = []
        for (infile, tree) in self.annotationtrees:
            for utterance in tree.getTree():
                if self.locale != None and utterance[4] != self.locale:
                    continue
                if self.participant != None and utterance[5] != self.participant:
                    continue
                for word in utterance[2]:
                    if len(word) > 0:
                        words.append(word[1])
        return words

    def sents(self):
        """
        Returns a list of sentences, which are lists of words from the
        corpus files.
        """
        sents = []
        for (infile, tree) in self.annotationtrees:
            for utterance in tree.getTree():
                if self.locale != None and utterance[4] != self.locale:
                    continue
                if self.participant != None and utterance[5] != self.participant:
                    continue
                words = []
                for word in utterance[2]:
                    if len(word) > 0:
                        words.append(word[1])
                if len(words) > 0:
                    sents.append(words)
        return sents

    def sentsWithTranslations(self):
        """
        Returns a list of (list of words, translation) tuples from the
        corpus files.
        """
        sents = []
        for (infile, tree) in self.annotationtrees:
            for utterance in tree.getTree():
                if self.locale != None and utterance[4] != self.locale:
                    continue
                if self.participant != None and utterance[5] != self.participant:
                    continue
                words = []
                for word in utterance[2]:
                    if len(word) > 0:
                        words.append(word[1])
                if len(words) > 0:
                    sents.append((words, utterance[3]))
        return sents


class PosCorpusReader(CorpusReader):
    """
    The class EafPosCorpusReader implements a part of the corpus reader API
    described in the Natual Language Toolkit (NLTK). The class reads in all
    the .eaf files (from the linguistics annotation software called Elan)
    in a given directory and makes this data accessible through
    several functions. The data contains "tags", which are annotations
    in "part of speech" tiers in Elan.
    The .eaf files must at least contain a tier with words.
    Access to the data is normally read-only.
    """
    
    def __init__(self, locale = None, participant = None, utterancetierTypes = None, wordtierTypes = None, postierTypes = None, translationtierTypes = None):
        """
        root: is the directory where your .eaf files are stored. Only the
            files in the given directory are read, there is no recursive
            reading right now. This parameter is obligatory.
        files: a regular expression for the filenames to read. The
            default value is "*.eaf"
        locale: restricts the corpus data to tiers with the given locale.
        participant: restricts the corpus data to tiers with the given
            particiapant.
        utterancetierType: the type of the tier you gave to your
            "utterances" in Elan. The EafTrees have several default values
            for this tier type: [ "utterance", "utterances", "Äußerung",
            "Äußerungen" ]. If you used a different tier type in Elan you
            can specify it as a parameter here. The parameter may either
            be a string or a list of strings.
        wordtierType: the type of the tier you gave to your
            "words" in Elan. The EafTrees have several default values
            for this tier type: [ "words", "word", "Wort", "Worte",
            "Wörter" ]. If you used a different tier type in Elan you
            can specify it as a parameter here. The parameter may either
            be a string or a list of strings.
        postierType: the type of the tier you gave to your
            "parts of speeches" in Elan. The EafTrees have several default
            values for this tier type: [ "part of speech", "parts of speech",
            "Wortart", "Wortarten" ]. If you used a different tier type in
            Elan you can specify it as a parameter here. The parameter
            may either be a string or a list of strings.
        """
        self.locale = locale
        self.participant = participant
        self.utterancetierTypes = utterancetierTypes
        self.wordtierTypes = wordtierTypes
        self.postierTypes = postierTypes
        self.morphemetierTypes = None
        self.glosstierTypes = None
        self.translationtierTypes = translationtierTypes
        self.interlineartype = POS
        self.annotationtrees = []

    def taggedWords(self):
        """
        Returns a list of (word, tag) tuples. Each tag is a list of
        parts of speech.
        """
        words = []
        for (infile, tree) in self.annotationtrees:
            for utterance in tree.getTree():
                if self.locale != None and utterance[4] != self.locale:
                    continue
                if self.participant != None and utterance[5] != self.participant:
                    continue
                for word in utterance[2]:
                    if len(word) > 0:
                        tag = []
                        for (id, pos) in word[2]:
                            tag.append(pos)
                        words.append((word[1], tag))
        return words

    def taggedSents(self):
        """
        Returns a list of (list of (word, tag) tuples). Each tag is a list
        of parts of speech.
        """
        sents = []
        for (infile, tree) in self.annotationtrees:
            for utterance in tree.getTree():
                if self.locale != None and utterance[4] != self.locale:
                    continue
                if self.participant != None and utterance[5] != self.participant:
                    continue
                words = []
                for word in utterance[2]:
                    if len(word) > 0:
                        tag = []
                        for id, pos in word[2]:
                            tag.append(pos)
                        words.append((word[1], tag))
                if len(words) > 0:
                    sents.append(words)
        return sents

    def taggedSentsWithTranslations(self):
        """
        Returns a list of (sentence, translation) tuples. Sentences
        are lists of (word, tag) tuples. Each tag is a list of
        parts of speech.
        """
        sents = []
        for (infile, tree) in self.annotationtrees:
            for utterance in tree.getTree():
                if self.locale != None and utterance[4] != self.locale:
                    continue
                if self.participant != None and utterance[5] != self.participant:
                    continue
                words = []
                for word in utterance[2]:
                    if len(word) > 0:
                        tag = []
                        for id, pos in word[2]:
                            tag.append(pos)
                        words.append((word[1], tag))
                if len(words) > 0:
                    sents.append((words, utterance[3]))
        return sents

class GlossCorpusReader(CorpusReader):
    """The class EafGlossCorpusReader implements a part of the corpus reader API
    described in the Natural Language Toolkit (NLTK). The class reads in all
    the .eaf files (from the linguistics annotation software called Elan)
    in a given directory and makes this data accessible through
    several functions. The data contains "tags", which are annotations
    in "morpheme" and "gloss" tiers in Elan.
    The .eaf files must at least contain a tier with words.
    Access to the data is normally read-only.
    """

    def __init__(self, locale = None, participant = None, utterancetierTypes = None, wordtierTypes = None, translationtierTypes = None, morphemetierTypes = None, glosstierTypes = None):
        """
        root: is the directory where your .eaf files are stored. Only the
            files in the given directory are read, there is no recursive
            reading right now. This parameter is obligatory.
        files: a regular expression for the filenames to read. The
            default value is "*.eaf"
        locale: restricts the corpus data to tiers with the given locale.
        participant: restricts the corpus data to tiers with the given
            particiapant.
        utterancetierTypes: the type of the tier you gave to your
            "utterances" in Elan. The EafTrees have several default values
            for this tier type: [ "utterance", "utterances", "Äußerung",
            "Äußerungen" ]. If you used a different tier type in Elan you
            can specify it as a parameter here. The parameter may either
            be a string or a list of strings.
        wordtierTypes: the type of the tier you gave to your
            "words" in Elan. The EafTrees have several default values
            for this tier type: [ "words", "word", "Wort", "Worte",
            "Wörter" ]. If you used a different tier type in Elan you
            can specify it as a parameter here. The parameter may either
            be a string or a list of strings.
        morphemetierTypes: the type of the tier you gave to your
            "morphemes" in Elan. The EafTrees have several default values
            for this tier type: [ "morpheme", "morphemes",  "Morphem",
            "Morpheme" ]. If you used a different tier type in Elan you
            can specify it as a parameter here. The parameter may either
            be a string or a list of strings.
        glosstierTypes: the type of the tier you gave to your
            "glosses" in Elan. The EafTrees have several default values
            for this tier type: [ "glosses", "gloss", "Glossen", "Gloss",
            "Glosse" ]. If you used a different tier type in Elan you
            can specify it as a parameter here. The parameter may either
            be a string or a list of strings.
        translationtierTypes: the type of the tier you gave to your
            "translations" in Elan. The EafTrees have several default values
            for this tier type: [  "translation", "translations",
            "Übersetzung",  "Übersetzungen" ]. If you used a different tier
            type in Elan you can specify it as a parameter here. The
            parameter may either be a string or a list of strings.
        """
        self.locale = locale
        self.participant = participant
        self.utterancetierTypes = utterancetierTypes
        self.wordtierTypes = wordtierTypes
        self.postierTypes = None
        self.morphemetierTypes = morphemetierTypes
        self.glosstierTypes = glosstierTypes
        self.translationtierTypes = translationtierTypes
        self.interlineartype = GLOSS
        self.annotationtrees = []

    def morphemes(self):
        """
        Returns a list of morphemes from the corpus files.
        """
        morphemes = []
        for (infile, tree) in self.annotationtrees:
            for utterance in tree.getTree():
                if self.locale != None and utterance[4] != self.locale:
                    continue
                if self.participant != None and utterance[5] != self.participant:
                    continue
                for word in utterance[2]:
                    if len(word) > 0:
                        for morpheme in word[2]:
                            if morpheme[1] != '':
                                morphemes.append(morpheme[1])
        return morphemes

    def taggedMorphemes(self):
        """
        Returns a list of (morpheme, list of glosses) tuples.
        """
        morphemes = []
        for (infile, tree) in self.annotationtrees:
            for utterance in tree.getTree():
                if self.locale != None and utterance[4] != self.locale:
                    continue
                if self.participant != None and utterance[5] != self.participant:
                    continue
                for word in utterance[2]:
                    if len(word) > 0:
                        for morpheme in word[2]:
                            if morpheme[1] != '':
                                glosses = []
                                for gloss in morpheme[2]:
                                    if gloss[1] != '':
                                        glosses.append(gloss[1])
                                morphemes.append((morpheme[1], glosses))
        return morphemes
        
    def taggedWords(self):
        """
        Returns a list of (word, tag) tuples. Each tag is a list of
        (morpheme, list of glosses) tuples.
        """
        words = []
        for (infile, tree) in self.annotationtrees:
            for utterance in tree.getTree():
                if self.locale != None and utterance[4] != self.locale:
                    continue
                if self.participant != None and utterance[5] != self.participant:
                    continue
                for word in utterance[2]:
                    if len(word) > 0:
                        tag = []
                        for morpheme in word[2]:
                            if morpheme[1] != '':
                                glosses = []
                                for gloss in morpheme[2]:
                                    if gloss[1] != '':
                                        glosses.append(gloss[1])
                                tag.append((morpheme[1], glosses))
                        words.append((word[1], tag))
        return words

    def taggedSents(self):
        """
        Returns a list of (list of (word, tag) tuples). Each tag is
        a list of (morpheme, list of glosses) tuples.
        """
        sents = []
        for (infile, tree) in self.annotationtrees:
            for utterance in tree.getTree():
                if self.locale != None and utterance[4] != self.locale:
                    continue
                if self.participant != None and utterance[5] != self.participant:
                    continue
                words = []
                for word in utterance[2]:
                    if len(word) > 0:
                        tag = []
                        for morpheme in word[2]:
                            if morpheme[1] != '':
                                glosses = []
                                for gloss in morpheme[2]:
                                    if gloss[1] != '':
                                        glosses.append(gloss[1])
                                tag.append((morpheme[1], glosses))
                        words.append((word[1], tag))
                if len(words) > 0:
                    sents.append(words)
        return sents

    def taggedSentsWithTranslations(self):
        """
        Returns a list of (sentence, translation) tuples. Sentences
        are lists of (word, tag) tuples. Each tag is a list of
        (morpheme, list of glosses) tuples.
        """
        sents = []
        for (infile, tree) in self.annotationtrees:
            for utterance in tree.getTree():
                if self.locale != None and utterance[4] != self.locale:
                    continue
                if self.participant != None and utterance[5] != self.participant:
                    continue
                words = []
                for word in utterance[2]:
                    if len(word) > 0:
                        tag = []
                        #print word
                        for morpheme in word[2]:
                            if morpheme[1] != '':
                                glosses = []
                                for gloss in morpheme[2]:
                                    if gloss[1] != '':
                                        glosses.append(gloss[1])
                                tag.append((morpheme[1], glosses))
                        words.append((word[1], tag))
                if len(words) > 0:
                    sents.append((words, utterance[3]))
        return sents

