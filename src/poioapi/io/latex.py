# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2014 Poio Project
# Author: Pedro Manha <pmanha@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

from __future__ import absolute_import
from __future__ import unicode_literals

import poioapi.io.graf
import poioapi.annotationgraph
import poioapi.data
import poioapi.mapper

import unicodedata
import os
import codecs

#the key is the result of calling ord() on the char
special_char_mapping = {
    779: '\\H{{{0}}}',
    '_': '\\_',
    'ʼ': '\'',
    'ƛ': ['tipa', '', '\\textcrlambda '],
    'ʎ': ['tipa', '', '\\textturny '],
    'ɣ': ['tipa', '', '\\textgamma '],
    'ħ': ['tipa', '', '\\textcrh '],
    'ɡ': 'g',
    'ɬ': 'ł',
    'ʔ': ['tipa', '', '\\textglotstop '],
    'ʕ': ['tipa', '', '\\textinvglotstop '],
    '#': '\\#'
}


class Writer(poioapi.io.graf.BaseWriter):

    def __init__(self):
        self._output_stream = None
        self._preamble = dict()
        self._document_class = 'article'
        self._dc_options = ['a4paper', '11pt']

    def _add_package(self, package, option=''):
        """ Method to add a latex package to the preamble.
            This is done this way to prevent loading unnecessary packages.

            Parameters
            ----------
            package : str
                The name of the package
            option : str
                The option to activate when loading the package
        """
        if package not in self._preamble.keys():
            self._preamble[package] = option

    def _write_preamble(self):
        """ Method to write out the document's preamble.
            Any packages that must appear in every document must be added here.
        """
        self._output_stream.write('\\documentclass[a4paper,11pt]{article}\n')
        self._output_stream.write('\\usepackage{ucs}\n')
        self._output_stream.write('\\usepackage[utf8x]{inputenc}\n')
        self._output_stream.write('\\usepackage[T1]{fontenc}\n')
        self._output_stream.write('\\usepackage{gb4n}\n')
        self._output_stream.write('\n')
        for package in self._preamble:
            pkg = '\\usepackage'
            if self._preamble[package] != '':
                pkg += '[' + self._preamble[package] + ']'
            pkg += '{' + package + '}\n'
            self._output_stream.write(pkg)

        self._output_stream.write('\n')

    def _build_tier_block(self, tier_identifier, converter, parent_node,
                          separator=' '):
        """ Function to build the presentation string of a tier.

            Parameters
            ----------
            tier_identifier : int
                One of the values of 'enum' of tier_labels from the data
                module.
            converter : poioapi.annotationgraph.AnnotationGraph
                The node storage
            parent_node : graf.Node
                The node for which to build the presentation string.
        """
        tier_nodes = self._all_nodes_for_tier(tier_identifier, converter,
                                              parent_node)

        tier_annotations = [converter.annotation_value_for_node(node)
                            for node in tier_nodes]

        tier_block = separator.join(tier_annotations)

        return {'block': tier_block, 'nodes': tier_nodes}

    def _build_lines_for_phrase(self, converter, phrase_node):
        """ Builds the line block for a given phrase.

            Parameters
            ----------
            converter : poioapi.annotationgraph.AnnotationGraph
                The node storage
            phrase_node : graf.Node
                The phrase for which to build the block for.

            Return
            ------
            ret : dict
                A dictionary of the lines for the phrase.
        """
        word_line = ''
        morpheme_line = ''
        gloss_line = ''
        ret = dict()
        word_nodes = self._all_nodes_for_tier(poioapi.data.TIER_WORD,
                                              converter, phrase_node)

        for word_node in word_nodes:
            word_annot = converter.annotation_value_for_node(word_node)
            word_line += word_annot + ' '

            pos_annots = self._build_tier_block(poioapi.data.TIER_POS,
                                                converter, word_node, '.')

            poses = pos_annots['block']

            children_block = self._build_morphemes(converter, word_node,
                                                   poses)

            morpheme_line += children_block[poioapi.data.TIER_MORPHEME] + ' '
            gloss_and_pos = children_block[poioapi.data.TIER_GLOSS]

            if poses != '':
                if gloss_and_pos != '':
                    gloss_and_pos += '-' + poses
                else:
                    gloss_and_pos = poses

            gloss_line += gloss_and_pos + ' '

        word_line = word_line.strip()
        morpheme_line = morpheme_line.strip()
        gloss_line = gloss_line.strip()

        ret['words'] = word_line
        ret['morpheme'] = morpheme_line
        ret['gloss'] = gloss_line

        translation_nodes = self._all_nodes_for_tier(
                poioapi.data.TIER_TRANSLATION, converter, phrase_node)
        if len(translation_nodes) > 0:
            ret['translation'] = converter.annotation_value_for_node(
                    translation_nodes[0])
        else:
            ret['translation'] = ''

        return ret

    def _build_morphemes(self, converter, word_node, pos_annots):
        """ Function to build the morpheme and gloss lines.

            Parameters
            ----------
            converter : poioapi.annotationgraph.AnnotationGraph
                The node storage
            word_node : graf.Node
                The word that is the parent of the morpheme(s).
            pos_annots : list of string
                The part-of-speech annotations for the word.
                They are outputted in the gloss line, and
                can be children of morphemes.
        """
        ret = dict()

        morpheme_block = self._build_tier_block(poioapi.data.TIER_MORPHEME,
                                                converter, word_node, '-')
        morpheme_nodes = morpheme_block['nodes']

        ret[poioapi.data.TIER_MORPHEME] = morpheme_block['block']
        gloss_blocks = [self.\
                            _build_morpheme_children(converter, morpheme_node,
                                                 pos_annots)
                        for morpheme_node in morpheme_nodes]

        ret[poioapi.data.TIER_GLOSS] = '-'.join(gloss_blocks)

        return ret

    def _build_morpheme_children(self, converter, morpheme_node, pos_annots):
        """ Function that builds the string representation for the gloss line.

            Parameters
            ----------
            converter : poioapi.annotationgraph.AnnotationGraph
                The node storage
            morpheme_node : graf.Node
                The morpheme that is the parent of the gloss(es)
                and/or the pos(es).
            pos_annots : list of string
                The part-of-speech annotations for the word.
                They are outputted in the gloss line, and
                can be children of morphemes.
        """
        gloss_pos_block = ''

        gloss_block = self._build_tier_block(poioapi.data.TIER_GLOSS,
                                             converter, morpheme_node, '.')
        gloss_pos_block += gloss_block['block']

        #if there are not any poses in the parameter already,
        #then they are children of morphemes
        if pos_annots == '':
            pos_block = self._build_tier_block(poioapi.data.TIER_POS,
                                               converter, morpheme_node, '.')
            pos_annots = pos_block['block']
            if pos_annots != '':
                if gloss_pos_block != '':
                    gloss_pos_block += '.'

                gloss_pos_block += pos_annots

        return gloss_pos_block

    def _format_for_latex(self, text):
        """ Function to sanitize text, so that it can be typeset by latex.
            This sanitation consists of three operations:
                1. Normalize the text to NFC.
                    This compresses diacritics where possible.
                2. Replacement of unknown unicode characters with a default.
                3. Replacement of non-typesettable character with their
                    latex counterpart or equivalent character.

            Parameters
            ----------
            text : str
                The text to sanitize.

            Returns
            -------
            The text after sanitation.
        """
        correct_line = ''
        normalized_line = unicodedata.normalize('NFC', text)
        for idx, c in enumerate(normalized_line):
            try:
                if unicodedata.combining(c) != 0:
                    continue
                next_char = normalized_line[idx+1]
                name = unicodedata.name(c, None)
                codepoint = ord(next_char)
                if codepoint in special_char_mapping.keys():
                    latex_command = special_char_mapping[codepoint]
                    correct_line += self._build_latex_replacement(latex_command, c)
                elif c in special_char_mapping.keys():
                    latex_command = special_char_mapping[c]
                    correct_line += self._build_latex_replacement(latex_command, c)
                elif name is None:
                    self._preamble['latexsym'] = ''
                    correct_line += '□'
                else:
                    correct_line += c
            except IndexError:
                if unicodedata.combining(c) != 0:
                    continue
                if c in special_char_mapping.keys():
                    latex_command = special_char_mapping[c]
                    correct_line += self._build_latex_replacement(latex_command, c)
                else:
                    correct_line += c

        return correct_line

    def _build_latex_replacement(self, value, cmd_param):
        """ Helper function that builds the latex or equivalent
            replacement for a character.


            Parameters
            ----------
            value : str
                The latex command.
            cmd_param : str
                The parameter for the command.

            Returns
            -------
            The built command. If the command has no
            parameters or if its a direct character
            replacement, the effective return is the value parameter
        """
        command = ''
        if isinstance(value, list):
            self._add_package(value[0], value[1])
            command = value[2]
        else:
            command = value

        return command.format(cmd_param)

    def _build_latex_body(self, converter, temp_file_name):
        """ Method that builds a temporary file that contains the latex
            body of the document. This is done to allow for document specific
            packages to be added to the preamble.

            Parameters
            ----------
            converter : poioapi.annotationgraph.AnnotationGraph
                The node storage
            temp_file_name : str
                The temporary file name.
        """
        temp_file = codecs.open(temp_file_name, 'w', encoding='utf8')

        root_nodes = converter.root_nodes()

        for node in root_nodes:
            temp_file.write('\\ea\n')
            tier_id = node.id.split('..')[0]
            if tier_id in converter.tier_mapper.tier_labels(poioapi.data.TIER_UTTERANCE):
                lines = self._build_lines_for_phrase(converter, node)
                temp_file.write('\\glll\n')
                temp_file.write(self._format_for_latex(
                    lines['words']) + '\\\\\n')
                temp_file.write(self._format_for_latex(
                    lines['morpheme']) + '\\\\\n')
                temp_file.write(self._format_for_latex(
                    lines['gloss']) + '\\\\\n')
                if lines['translation'] != '':
                    temp_file.write('\\glt{} ' + self._format_for_latex(
                        lines['translation']) + '\\\\\n')
            else:
                phrases = self._all_nodes_for_tier(poioapi.data.TIER_UTTERANCE,
                                                converter, node)
                root_annot = converter.annotation_value_for_node(node)
                root_annot = self._format_for_latex(root_annot)
                temp_file.write('\\ref {0}\\\\\n'.format(root_annot))

                for phrase in phrases:
                    lines = self._build_lines_for_phrase(converter, phrase)
                    temp_file.write('\\glll\n')
                    temp_file.write(self._format_for_latex(
                    lines['words']) + '\\\\\n')
                    temp_file.write(self._format_for_latex(
                        lines['morpheme']) + '\\\\\n')
                    temp_file.write(self._format_for_latex(
                        lines['gloss']) + '\\\\\n')
                    if lines['translation'] != '':
                        temp_file.write('\\glt{} ' + self._format_for_latex(
                            lines['translation'] + '\\\\\n'))

            temp_file.write('\\z\n')

        temp_file.close()

    def write(self, outputfile, converter):
        """ Method to write the latex document.

            Parameters
            ----------
            ouputfile : str
                The destination filepath.
            converter : poioapi.annotationgraph.AnnotationGraph
                The node storage.
        """
        self._output_stream = codecs.open(outputfile, 'w', encoding='utf8')

        #build the document body
        temp_file = outputfile + '.tmp'
        self._build_latex_body(converter, temp_file)

        #write the final document
        self._write_preamble()

        self._output_stream.write('\\begin{document}\n')

        for line in codecs.open(temp_file, 'r', encoding='utf8'):
            self._output_stream.write(line)

        os.remove(temp_file)

        self._output_stream.write('\\end{document}')

        self._output_stream.close()

    def _all_nodes_for_tier(self, tier_identifier, converter, parent_node):
        """ Helper function to get all the node for an annotation_tier.

            Parameters
            ----------
            tier_identifier : int
                One of the values of 'enum' of tier_labels from the data
                module.
            converter : poioapi.annotationgraph.AnnotationGraph
                The node storage.
        """
        tier_nodes = []
        tier_tags = converter.tier_mapper.tier_labels(tier_identifier)
        for tag in tier_tags:
            nodes = converter.nodes_for_tier(tag, parent_node)
            for node in nodes:
                if node not in tier_nodes:
                    tier_nodes.append(node)

        return tier_nodes