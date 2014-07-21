# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

"""This module contains classes to access to
parse and generate Typecraft files from a
GrAF object.
"""

from __future__ import absolute_import
from __future__ import unicode_literals

import codecs
import time
import datetime
import re
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring
from xml.dom import minidom

import poioapi.io.graf
import poioapi.annotationgraph
import poioapi.data
import poioapi.mapper

# Tier map
tier_map = {
    poioapi.data.TIER_UTTERANCE: ['phrase', 'utterance_gen'],
    poioapi.data.TIER_WORD: ['word', 't'],
    poioapi.data.TIER_MORPHEME: ['morpheme', 'm'],
    poioapi.data.TIER_POS: ['pos', 'p'],
    poioapi.data.TIER_GLOSS: ['gloss', 'g'],
    poioapi.data.TIER_TRANSLATION: ['translation', 'f'],
    poioapi.data.TIER_COMMENT: ['comment', 'nt']
}

class Parser(poioapi.io.graf.BaseParser):
    """
    Class that will handle the parse of
    Typecraft files.

    """

    def __init__(self, filepath):
        """Class's constructor.

        Parameters
        ----------
        filepath : str
            Path of the typecraft file.

        """

        self.filepath = filepath
        self.parse()

    def parse(self):
        """This method it will parse the Typecraft
        file.

        """

        self.nodetree = ET.parse(self.filepath)
        self.tree = self.nodetree.getroot()
        self.namespace = {'xmlns': re.findall(r"\{(.*?)\}", self.tree.tag)[0]}
        self._current_id = 0
        self._elements_map = {"phrase": [], "word": [], "translation": [],
                              "description": [], "pos": [], "morpheme": [],
                              "gloss": []}

        self.parse_element_tree(self.tree)

    def parse_element_tree(self, tree):
        """This method it will parse the XML elements
        into a map. It also create ids for the child
        elements since they are not present in the
        XML.

        """

        for element in tree:
            if element.tag == "{" + self.namespace['xmlns'] + "}" + "phrase":
                self._elements_map["phrase"].append({"id": element.attrib["id"],
                                                     "attrib": element.attrib})
                self._current_phrase_id = element.attrib["id"]
            elif element.tag == "{" + self.namespace['xmlns'] + "}" + "original":
                for i, el in enumerate(self._elements_map["phrase"]):
                    if el["id"] == self._current_phrase_id:
                        el["value"] = element.text
                        self._elements_map["phrase"][0] = el

            elif element.tag == "{" + self.namespace['xmlns'] + "}" + "word":
                self._current_word_id = self._next_id()
                self._elements_map["word"].append({"id": self._current_word_id,
                                                   "attrib": element.attrib,
                                                   "parent": self._current_phrase_id})
            elif element.tag == "{" + self.namespace['xmlns'] + "}" + "pos":
                self._elements_map["pos"].append({"id": self._next_id(),
                                                  "value": element.text,
                                                  "parent": self._current_word_id})
            elif element.tag == "{" + self.namespace['xmlns'] + "}" + "morpheme":
                self._current_morpheme_id = self._next_id()
                self._elements_map["morpheme"].append({"id": self._current_morpheme_id,
                                                       "attrib": element.attrib,
                                                       "parent": self._current_word_id})
            elif element.tag == "{" + self.namespace['xmlns'] + "}" + "gloss":
                self._elements_map["gloss"].append({"id": self._next_id(),
                                                    "value": element.text,
                                                    "parent": self._current_morpheme_id})
            elif element.tag == "{" + self.namespace['xmlns'] + "}" + "description":
                self._elements_map["description"].append({"id": self._next_id(),
                                                          "value": element.text,
                                                          "parent": self._current_phrase_id})
            elif element.tag == "{" + self.namespace['xmlns'] + "}" + "translation":
                self._elements_map["translation"].append({"id": self._next_id(),
                                                          "value": element.text,
                                                          "parent": self._current_phrase_id})
            if len(element.getchildren()) > 0:
                self.parse_element_tree(element)

    def get_root_tiers(self):
        return [poioapi.io.graf.Tier("phrase")]

    def get_child_tiers_for_tier(self, tier):
        if tier.name == "phrase":
            return [poioapi.io.graf.Tier("word"),
                    poioapi.io.graf.Tier("translation"),
                    poioapi.io.graf.Tier("description")]

        elif tier.name == "word":
            return [poioapi.io.graf.Tier("pos"),
                    poioapi.io.graf.Tier("morpheme")]

        elif tier.name == "morpheme":
            return [poioapi.io.graf.Tier("gloss")]

    def get_annotations_for_tier(self, tier, annotation_parent=None):
        if tier.name == "phrase":
            return [poioapi.io.graf.Annotation(e["id"], e["value"],
                                               self._get_features(e["attrib"]))
                    for e in self._elements_map[tier.name]]

        elif tier.name == "word" or tier.name == "morpheme":
            annotations = []
            for e in self._elements_map[tier.name]:
                if e["parent"] == annotation_parent.id:
                    features = self._get_features(e["attrib"])
                    value = e["attrib"]["text"]
                    annotations.append(poioapi.io.graf.Annotation(e["id"],
                        value, features))

            return annotations

        else:
            return [poioapi.io.graf.Annotation(e["id"], e["value"])
                    for e in self._elements_map[tier.name]
                    if e["parent"] == annotation_parent.id]

    def get_primary_data(self):
        """This method gets the information about
        the source data file which in this case is
        going to be always unknown.

        Returns
        -------
        primary_data : object
            PrimaryData object.

        """

        primary_data = poioapi.io.graf.PrimaryData()
        primary_data.type = poioapi.io.graf.NONE
        primary_data.filename = "unknown"

        return primary_data

    def _get_features(self, attributes):
        """This method gets the attribute data from
        the tag elements.

        """

        features = {}

        for key, value in attributes.items():
            if key != "id":
                if key != "text":
                    features[key] = value

        return features

    def _next_id(self):
        current_id = str(int(self._current_id) + 1)
        self._current_id = current_id

        return current_id

    def region_for_annotation(self, annotation):
        pass

    def tier_has_regions(self, tier):
        pass

class Writer(poioapi.io.graf.BaseWriter):
    """
    A writer for Typecraft XML.

    """


    def __init__(self):
        self._phrases = []

        self._missing_glosses = {}
        self._missing_poses = {}
        self._current_text_id = 0
        self._current_phrase_id = 0
        self.extra_gloss_map = []
        self.extra_pos_map = []
        #The path of the JSON file containing the extra maps
        self._additional_maps_file = ''
        #the XML nodes
        self._root = None
        self._text = None
        self._phrase_element = None
        self._word_element = None
        self._pos_element = None
        self._morpheme_element = None
        self._annotation_mapper = None
        self._source_tier_names = None

        self._elan_begin_nodes = None
        self._elan_end_nodes = None
        self._elan_participant_nodes = None


    def _init_root_node(self):
        """ Method to initialize the root node to which add all the subelements.
        """
        self._root = ET.Element("typecraft", {"xsi:schemaLocation": "http://typecraft.org/typecraft.xsd",
                   "xmlns": "http://typecraft.org/typecraft",
                   "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance"})

    def _create_text_node(self, language='und', original_title='Empty Title', translation_title=''):
        """ Method to create the 'text' node and set some information about the node.
            Assumes that the 'root' node is already initiated.

            Parameters
            ----------
            language : str
            the language in which the original text is written.

            original_title : str
            The title of the text in the original language

            translation_title : str
            The title of the text in the translation language
        """

        self._text = ET.SubElement(self._root, "text", {"id": self._next_text_id(),
            "lang": language})

        ET.SubElement(self._text, "title").text = original_title
        ET.SubElement(self._text, "titleTranslation").text = translation_title

    def write(self, outputfile, converter, pretty_print=False,
              extra_tag_map='', language='und'):
        """Writer for the Typecraft file. This method evaluate
        if all the Glosses and POS in the GrAF are validated
        against two specific Typecraft lists.

        Parameters
        ----------
        outputfile : str
            The output file name.
        converter : Converter
            Converter object from Poio API.
        pretty_print : boolean
            Boolean to set the XML pretty print.
        missing : boolean
            Whether to output the missing tags or not.
        extra_tag_map : str
            The path of the JSON file containing the extra maps
        language : str
            The ISO 639-3 code of the source's language

        """

        self._additional_maps_file = extra_tag_map

        self._annotation_mapper = poioapi.mapper.AnnotationMapper(
            converter.source_type, poioapi.data.TYPECRAFT)
        self._annotation_mapper.load_mappings(extra_tag_map)

        phrase_nodes = []
        if converter.source_type == poioapi.data.TOOLBOX:
            ref_nodes = converter.nodes_for_tier('ref')
            for ref in ref_nodes:

                for marker in converter.tier_mapper.tier_labels(
                        poioapi.data.TIER_UTTERANCE):
                    phrase_nodes.extend(converter.nodes_for_tier(marker, ref))

                # get the ELAN  specific nodes. assuming that only toolbox has them
                self._elan_begin_nodes = converter.nodes_for_tier('ELANBegin', ref)
                self._elan_end_nodes = converter.nodes_for_tier('ELANEnd', ref)
                self._elan_participant_nodes = converter.nodes_for_tier('ELANParticipant', ref)
        else:
            for marker in converter.tier_mapper.tier_labels(
                    poioapi.data.TIER_UTTERANCE):
                phrase_nodes.extend(converter.nodes_for_tier(marker, None))
        self._init_root_node()
        self._create_text_node(language=language)

        ET.SubElement(self._text, 'body').text = ' '.join(
            [converter.annotation_value_for_node(phrase) for phrase in
             phrase_nodes])
        for phrase in phrase_nodes:

            annotation = converter.annotation_value_for_node(phrase)
            if annotation == '':
                continue

            self._phrase_element = ET.SubElement(self._text, 'phrase',
                                                 {'id': self._next_phrase_id(),
                                                  'valid': 'VALID'})

            # handle ELAN data, only when converting from toolbox
            if converter.source_type == poioapi.data.TOOLBOX:
                self._write_elan_attributes(converter)

            ET.SubElement(self._phrase_element, 'original').text = annotation

            #add the translation, description and globaltags subelements
            self._write_translations(converter, phrase)

            ET.SubElement(self._phrase_element, 'description')
            ET.SubElement(self._phrase_element, 'globaltags',
                          {'id': '1', 'tagset': 'Default'})

            #get the word nodes for the current phrase
            self._write_words(converter, phrase)

        self.write_xml(self._root, outputfile)

    def _write_words(self, converter, phrase):
        """ Method to build the word nodes of the XML.

            Parameters
            ----------
            converter : poioapi.annotationgraph.AnnotationGraph
                Converter object from Poio API.
            phrase : graf.Node
                The parent node of the words
        """

        word_tier_markers = converter.tier_mapper.tier_labels(
            poioapi.data.TIER_WORD)
        word_nodes = []
        for marker in word_tier_markers:
            word_nodes.extend(converter.nodes_for_tier(marker, phrase))

        for word in word_nodes:
            annotation = converter.annotation_value_for_node(word)
            annotation = annotation.replace('-', '')
            self._word_element = ET.SubElement(self._phrase_element, 'word',
                                               {'text': annotation,
                                                'head': 'false'})

            #adding the part-of-speech (pos) element
            self._pos_element = ET.SubElement(self._word_element, 'pos')
            self._write_pos(converter, word)
            if self._pos_element.text == '':
                check_pos_in_morphemes = True
            else:
                check_pos_in_morphemes = False

            #extract the morpheme nodes for the current word
            self._write_morphemes(converter, word, check_pos_in_morphemes)

    def _write_elan_attributes(self, converter):
        """ Writes the ELAN information for toolbox files.

            Parameters
            ----------
            :param converter: str
                The source for the attributes
        """
        if len(self._elan_begin_nodes) == 0 \
                and len(self._elan_end_nodes) == 0 \
                and len(self._elan_participant_nodes) == 0:
            return
        begin_node = self._elan_begin_nodes[0]
        end_node = self._elan_end_nodes[0]
        participant_node = self._elan_participant_nodes[0]
        begin_annotation = converter.annotation_value_for_node(begin_node)
        end_annotation = converter.annotation_value_for_node(end_node)
        participant_annotation = converter.annotation_value_for_node(participant_node)

        begin_time = self._string_to_milliseconds(begin_annotation)
        end_time = self._string_to_milliseconds(end_annotation)

        duration = end_time - begin_time

        self._phrase_element.set('offset', str(begin_time))
        self._phrase_element.set('duration', str(duration))
        self._phrase_element.set('speaker', participant_annotation)

    def _write_pos(self, converter, parent_node):
        """ Method to build the word nodes of the XML.

            Parameters
            ----------
            converter : poioapi.annotationgraph.AnnotationGraph
                Converter object from Poio API.
            word : graf.Node
                The parent node of the part of speech tags
        """

        pos_annotations = []
        for marker in converter.tier_mapper.tier_labels(poioapi.data.TIER_POS):
            pos_annotations.extend(converter.annotations_for_tier(marker,
                                                                  parent_node))

        if len(pos_annotations) == 1:
            annotation = converter.annotation_value_for_annotation(
                pos_annotations[0])
            if not any((c in annotation) for c in "()/\.-?*"):
                mapping = self._annotation_mapper.validate_tag(
                    poioapi.data.TIER_POS, annotation)
                if mapping is None:
                    self._annotation_mapper.add_to_missing(
                        poioapi.data.TIER_POS, annotation)
                else:
                    self._pos_element.text = mapping
        else:
            self._pos_element.text = ''

    def _write_morphemes(self, converter, word, check_for_pos=False):
        """ Method to build the morpheme nodes of the XML.

            Parameters
            ----------
            converter : poioapi.annotationgraph.AnnotationGraph
                Converter object from Poio API.
            word : graf.Node
                The parent node of the words
        """
        morpheme_nodes = []
        for marker in converter.tier_mapper.tier_labels(
                poioapi.data.TIER_MORPHEME):
            morpheme_nodes.extend(converter.nodes_for_tier(marker, word))

        for morpheme in morpheme_nodes:
            annotation = converter.annotation_value_for_node(morpheme)
            annotation = annotation.replace('-', '')

            if check_for_pos is True:
                self._write_pos(converter, morpheme)

            self._morpheme_element = ET.SubElement(self._word_element,
                                                   'morpheme',
                                                   {'text': annotation,
                                                    'baseform': annotation})
            self._write_gloss(converter, morpheme)

        if self._word_element.find('morpheme') is None:
            ET.SubElement(self._word_element, 'morpheme')

    def _write_gloss(self, converter, morpheme):
        """ Method to build the word nodes of the XML.

            Parameters
            ----------
            converter : poioapi.annotationgraph.AnnotationGraph
                Converter object from Poio API.
            morpheme : graf.Node
                The parent node of the words
        """
        gloss_annotations = []
        for marker in converter.tier_mapper.tier_labels(poioapi.data.TIER_GLOSS):
            gloss_annotations.extend(converter.annotations_for_tier(marker,
                                                                    morpheme))

        for gloss in gloss_annotations:
            annotation = converter.annotation_value_for_annotation(gloss)
            annotation = annotation.replace('-', '')

            splitter = '.'
            # Special gloss value
            if "?" in annotation and annotation != "?IPFV":
                return None

            # Select the splitter for the gloss values
            if ":" in annotation:
                splitter = ":"

            for token in annotation.split(splitter):
                gloss_list = self._annotation_mapper.validate_tag(
                    poioapi.data.TIER_GLOSS, token)

                if gloss_list is not None:
                    #if the tag is in the wrong tier, then put it in the
                    # correct tier. For now only detects POS
                    if isinstance(gloss_list, tuple) and len(gloss_list) == 2:
                        if gloss_list[0] in converter.tier_mapper.tier_labels(
                                poioapi.data.TIER_POS):
                            self._pos_element.text = gloss_list[1]
                    else:
                        self._split_destination_tags(gloss_list)

                else:
                    if not annotation.isupper():
                        if ":" in annotation:
                            annotation = annotation.split(":")[0]
                        elif "-" in annotation:
                            annotation = annotation.split("-")[0]
                        elif "/" in annotation:
                            annotation = annotation.split("/")[0]
                        self._morpheme_element.set("meaning", annotation)
                    else:
                        self._annotation_mapper.add_to_missing(
                            poioapi.data.TIER_GLOSS, token)

    def _split_destination_tags(self, tags):
        tokens = re.split(poioapi.mapper.tag_separators, tags)
        for token in tokens:
            ET.SubElement(self._morpheme_element, 'gloss').text = token

    def _write_translations(self, converter, phrase):
        """ Method to build the word nodes of the XML.

            Parameters
            ----------
            converter : poioapi.annotationgraph.AnnotationGraph
                Converter object from Poio API.
            phrase : graf.Node
                The parent node of the words
        """
        translation_annotations = []
        for marker in converter.tier_mapper.tier_labels(poioapi.data.TIER_TRANSLATION):
            translation_annotations.extend(converter.annotations_for_tier(marker, phrase))

        if len(translation_annotations) == 1:
            ET.SubElement(self._phrase_element, 'translation').text = \
                converter.annotation_value_for_annotation(translation_annotations[0])
        else:
            ET.SubElement(self._phrase_element, 'translation')

    def write_xml(self, root, outputfile, pretty_print=True):
        """Write the final Typecraft XML file.

        Parameters
        ----------
        root : ElementTree
            The root Typecraft element.
        outputfile : str
            The output file name.
        pretty_print : boolean
            Boolean to set the XML pretty print.

        """

        if pretty_print:
            doc = minidom.parseString(tostring(root))

            text_re = re.compile(r'>\n\s+([^<>\s].*?)\n\s+</', re.DOTALL)
            pretty_xml = text_re.sub(r'>\g<1></', doc.toprettyxml(indent='  '))

            file = codecs.open(outputfile, 'wb', encoding='utf-8')
            file.write(pretty_xml)
            file.close()
        else:
            tree = ET.ElementTree(root)
            tree.write(outputfile)

    def _string_to_milliseconds(self, value):
        """Convert a string to milliseconds. Time unit
        for the time values in Typecaft.

        Parameters
        ----------
        time_node : str
            The value to convert.

        Returns
        -------
        offset : int
            The offset value.

        """

        time_start = value.split(".")

        microseconds = int(time_start[1])
        try:
            x = time.strptime(time_start[0], '%H:%M:%S')

            offset = int(datetime.timedelta(hours=x.tm_hour, minutes=x.tm_min,
                seconds=x.tm_sec).seconds * 1000) + microseconds
        except ValueError:
            offset = (int(time_start[0]) * 1000) + microseconds

        return offset

    def _next_text_id(self):
        """Increment the text id.

        """

        current_id = str(int(self._current_text_id) + 1)
        self._current_text_id = current_id

        return str(current_id)

    def _next_phrase_id(self):
        """Increment the phrase id.

        """

        current_id = str(int(self._current_phrase_id) + 1)
        self._current_phrase_id = current_id

        return str(current_id)

    def missing_tags(self, outputfile, annotation_graph, additional_map_path):
        """ Method to check if all the poses and glosses are mapped in the external mapping provided.
            Any non-mapped gloss and/or pos tags are stored for outputting the JSON file.
            If no missing tags are found, the objects in the output file will be empty.
            If no tag mapping is passed (e.g. running the converter without the -t flag) then the result will
            contain all the tags.
        """

        #load the nodes to be validated
        pos_nodes = []
        for marker in annotation_graph.tier_mapper.tier_labels(poioapi.data.TIER_POS):
            pos_nodes.extend(annotation_graph.nodes_for_tier(marker))

        gloss_nodes = []
        for marker in annotation_graph.tier_mapper.tier_labels(poioapi.data.TIER_GLOSS):
            gloss_nodes.extend(annotation_graph.nodes_for_tier(marker))

        if self._annotation_mapper is None:
            self._annotation_mapper = \
                poioapi.mapper.AnnotationMapper(annotation_graph.source_type, poioapi.data.TYPECRAFT)

        # load the additional mappings if any
        self._annotation_mapper.load_mappings(additional_map_path)

        # done loading, now validate the tags
        # pos
        for node in pos_nodes:
            annotation = annotation_graph.annotation_value_for_node(node)
            # av = av.strip('-')
            # if self._annotation_mapper.validate_tag(poioapi.data.TIER_POS, av) is None and av.isupper():
            #     self._annotation_mapper.add_to_missing(poioapi.data.TIER_POS, av.upper())

            if not any((c in annotation) for c in "()/\.-?*"):
                mapping = self._annotation_mapper.validate_tag(poioapi.data.TIER_POS, annotation)
                if mapping is None:
                    self._annotation_mapper.add_to_missing(poioapi.data.TIER_POS, annotation)

        #gloss
        for node in gloss_nodes:
            annotation = annotation_graph.annotation_value_for_node(node)
            # av = av.strip('-')

            splitter = '.'
            # Special gloss value
            if "?" in annotation and annotation != "?IPFV":
                return None

            # Select the splitter for the gloss values
            if ":" in annotation:
                splitter = ":"

            for token in annotation.split(splitter):
                gloss_list = self._annotation_mapper.validate_tag(poioapi.data.TIER_GLOSS, token.strip('-'))

                if gloss_list is None and (token.isupper() or token.strip('-').isdigit()):
                    self._annotation_mapper.add_to_missing(poioapi.data.TIER_GLOSS, token.strip('-'))

        self._annotation_mapper.export_missing_tags(outputfile)