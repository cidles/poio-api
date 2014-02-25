# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

"""This module contains classes to access to
Typecraf files and generate GrAF files.
"""

from __future__ import absolute_import
import codecs
import time
import datetime
import re
import ast

import xml.etree.cElementTree as ET
from xml.etree.ElementTree import tostring
from xml.dom import minidom

import poioapi.io.graf


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
        self.tree = ET.parse(self.filepath).getroot()
        self.namespace = {'xmlns': re.findall(r"\{(.*?)\}", self.tree.tag)[0]}
        self._current_id = 0
        self._elements_map = {"phrase": [], "word": [], "translation": [],
                              "description": [], "pos": [], "morpheme": [],
                              "gloss": []}

        self.parse_element_tree(self.tree)

    def parse_element_tree(self, tree):
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
        the source data file.

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

    """

    def __init__(self):
        self._missing_gloss_list = []
        self._missing_pos_list = []
        self._current_text_id = 0
        self._current_phrase_id = 0
        self.language = "und"
        self.extra_gloss_map = None
        self.extra_pos_map = None

    def write(self, outputfile, converter, pretty_print=False, more_info=None, tags=None):
        nodes = converter.graf.nodes
        phrases = self._get_phrases(nodes, converter)
        time_start_nodes = self._get_tag_nodes(nodes, "ELANBegin")
        time_end_nodes = self._get_tag_nodes(nodes, "ELANEnd")
        participant_nodes = self._get_tag_nodes(nodes, "ELANParticipant")
        word_nodes = self._get_tag_nodes(nodes, "t")
        pos_nodes = self._get_tag_nodes(nodes, "p")
        morph_nodes = self._get_tag_nodes(nodes, "m")
        gloss_nodes = self._get_tag_nodes(nodes, "g")
        trans_nodes = self._get_tag_nodes(nodes, "f")

        if more_info:
            more_info = more_info.replace(":", "\":\"").replace("/", "\",\"").replace("{", "{\"").replace("}", "\"}")
            more_info = ast.literal_eval(more_info)

            self._current_text_id = more_info["ids"].split("-")[0]
            self._current_phrase_id = more_info["ids"].split("-")[1]
            self.language = more_info["lang"]

        if tags and tags != "null":
            tags = tags.replace(":", "\":\"").replace("/", "\",\"").replace("{", "{\"").replace("}", "\"}")

            if tags.split("_")[0] != "{EMPTY}":
                self.extra_gloss_map = ast.literal_eval(tags.split("_")[0])
            if tags.split("_")[1] != "{\"EMPTY\"}":
                self.extra_pos_map = ast.literal_eval(tags.split("_")[1])

        attribs = {"xsi:schemaLocation": "http://typecraft.org/typecraft.xsd",
                   "xmlns": "http://typecraft.org/typecraft",
                   "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance"}

        root = ET.Element("typecraft", attribs)

        # The language must be set as und
        text = ET.SubElement(root, "text", {"id": self._next_text_id(), "lang": self.language})

        if converter.meta_information:
            ET.SubElement(text, "title").text = converter.meta_information
        else:
            ET.SubElement(text, "title").text = "Empty Title"

        ET.SubElement(text, "titleTranslation")
        ET.SubElement(text, "body").text = self._get_body(phrases)

        for p in phrases:
            original = p.annotations._elements[0].features["annotation_value"]

            if original == "":
                continue

            phrase = ET.SubElement(text, "phrase", {"id": self._next_phrase_id(), "valid": "VALID"})

            offset_node = self._get_time_related_nodes(time_start_nodes, p)
            duration_node = self._get_time_related_nodes(time_end_nodes, p)
            participant_node = self._get_time_related_nodes(participant_nodes, p)

            # Get the time
            if offset_node:
                offset_value = self._string_to_milliseconds(offset_node)
                phrase.set("offset", str(offset_value))

                if duration_node:
                    duration_value = self._string_to_milliseconds(duration_node) - offset_value
                    phrase.set("duration", str(duration_value))

            if participant_node:
                phrase.set("speaker", participant_node.annotations._elements[0].features["annotation_value"])

            ET.SubElement(phrase, "original").text = original

            t = self._get_nodes_by_parent(trans_nodes, p.id)
            if t:
                ET.SubElement(phrase, "translation").text = t[0].annotations._elements[0].features["annotation_value"]
            else:
                ET.SubElement(phrase, "translation")

            ET.SubElement(phrase, "description")
            ET.SubElement(phrase, "globaltags", {"id": "1", "tagset": "Default"})

            for w in self._get_nodes_by_parent(word_nodes, p.id):
                w_value = w.annotations._elements[0].features["annotation_value"]
                
                word = ET.SubElement(phrase, "word", {"text": w_value, "head": "false"})
                p_value = self._get_pos_value(pos_nodes, w.id)

                if p_value is not "":
                    val = self._validate_pos(p_value, self.extra_pos_map)
                    if val != "NULL":
                        ET.SubElement(word, "pos").text = val

                for m in self._get_nodes_by_parent(morph_nodes, w.id):
                    m_value = m.annotations._elements[0].features["annotation_value"].replace("-", "")

                    morpheme = ET.SubElement(word, "morpheme", {"text": m_value, "baseform": m_value})

                    for g in self._get_nodes_by_parent(gloss_nodes, m.id):
                        if g.annotations._elements[0].features:
                            g_value = g.annotations._elements[0].features["annotation_value"].replace("-","")

                            gloss_list = self._validate_gloss(g_value.replace("-", ""), self.extra_gloss_map)

                            if gloss_list:
                                for gloss in gloss_list:
                                    if gloss != "NULL":
                                        ET.SubElement(morpheme, "gloss").text = gloss
                            else:
                                morpheme.set("meaning", self._set_meaning(g_value))

        if self._missing_gloss_list or self._missing_pos_list:
            self.write_missing_tags(outputfile)
        else:
            self.write_xml(root, outputfile)

    def write_missing_tags(self, outputfile):
        wrt = ""

        if self._missing_gloss_list:
            wrt += str(self._missing_gloss_list) + "--"
        if self._missing_pos_list:
            if wrt == "":
                wrt += "[]--" + str(self._missing_pos_list)
            else:
                wrt += str(self._missing_pos_list)
        else:
            wrt += "[]"

        if wrt != "":
            file = codecs.open(outputfile + ".missing", 'wb', encoding='utf-8')
            file.write(wrt)
            file.close()

    def write_xml(self, root, outputfile, pretty_print=True):
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

    def _get_phrases(self, nodes, converter):
        if "utterance_gen" in self._flatten_hierarchy_elements(converter.tier_hierarchies):
            result_nodes = [node for node in nodes if node.id.startswith("utterance_gen")]
        else:
            result_nodes = [node for node in nodes if node.id.startswith("ref")]

        return sorted(result_nodes, key=lambda node: int(node.id.split("..na")[1]))

    def _get_tag_nodes(self, nodes, tag):
        result_nodes = [node for node in nodes if node.id.startswith(tag)]

        return sorted(result_nodes, key=lambda node: int(node.id.split("..na")[1]))

    def _get_nodes_by_parent(self, nodes, parent_id):
        return [node for node in nodes if node.parent.id == parent_id]

    def _get_body(self, phrases, body=""):
        for n in phrases:
            body += n.annotations._elements[0].features["annotation_value"]

        return body

    def _get_pos_value(self, pos_nodes, parent_id):
        for node in pos_nodes:
            if node.parent.id == parent_id or node.parent.parent.id == parent_id:
                if node.annotations._elements[0].features:
                    pos_value = node.annotations._elements[0].features["annotation_value"]

                    if not any((c in pos_value) for c in "-,=:?*"):
                        return pos_value

        return ""

    def _get_time_related_nodes(self, time_nodes, parent_node):
        for node in time_nodes:
            if node.parent.id == parent_node.parent.id:
                return node

    def _string_to_milliseconds(self, time_node):
        time_start = time_node.annotations._elements[0].features["annotation_value"].split(".")

        microseconds = int(time_start[1])

        x = time.strptime(time_start[0], '%H:%M:%S')

        offset = int(datetime.timedelta(hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).seconds
                     * 1000) + microseconds

        return offset

    def _next_text_id(self):
        current_id = str(int(self._current_text_id) + 1)
        self._current_text_id = current_id

        return str(current_id)

    def _set_meaning(self, value):
        result = value

        if ":" in value:
            result = value.split(":")[0]
        elif "-" in value:
            result = value.split("-")[0]
        elif "/" in value:
            result = value.split("/")[0]

        return result

    def _next_phrase_id(self):
        current_id = str(int(self._current_phrase_id) + 1)
        self._current_phrase_id = current_id

        return str(current_id)

    def _flatten_hierarchy_elements(self, elements):
        """Flat the elements appended to a new list of elements.

        Parameters
        ----------
        elements : array_like
            An array of string values.

        Returns
        -------
        flat_elements : array_like
            An array of flattened `elements`.

        """

        flat_elements = []
        for e in elements:
            if type(e) is list:
                flat_elements.extend(self._flatten_hierarchy_elements(e))
            else:
                flat_elements.append(e)
        return flat_elements

    def _validate_pos(self, pos_value, extra_pos_map=None):
        """
        This function validates the pos value
        in a pos list from the TC pos list.
        """

        pos_list = ["PNposs", "N", "V", "PN", "ADVm", "Np", "PREP", "CN", "PRT", "COMP", "AUX", "CONJS", "QUANT",
                    "NMASC", "NNO", "NNEUT", "COP", "ART", "MOD", "PPOST", "ADJ", "DEM", "ADJC", "PNrefl", "DET", "Wh",
                    "Vtr", "Vitr", "PROposs", "P", "Vdtr", "CARD", "NDV", "CL", "ADVplc", "V3", "PRTposs", "V4",
                    "ADVtemp", "V2", "NUM", "REL", "EXPL", "CONJC", "Vmod", "Vlght", "PNana", "PROint", "PNrel",
                    "VtrOBL", "COPident", "PRTpred", "Nspat", "ORD", "PTCP", "CONJ", "PRTint", "Vneg", "PREPtemp",
                    "PREPdir", "NFEM", "PRtinf", "Ncomm", "Nbare", "Vcon", "PRTv", "PRTn", "ADVneg", "Vpre", "NUMpart",
                    "ADJS", "PRTexist", "CLFnum", "CLFnom", "CIRCP", "V1", "PREP/PROspt", "PRTprst", "Vvector", "PNdem",
                    "Nrel", "IPHON", "ADV", "VitrOBL", "Vimprs", "Vrefl", "PNabs", "Vbid", "Vvec", "INTRJCT"]

        pos_map = {"prn": "PN", "interj": "INTRJCT", "CVB": "Vcon", "pron": "PN", "part": "PRT", "intj": "INTRJCT",
                   "name": "Np", "encl": "CL", "pred": "COP"}

        value = None

        if not any((c in pos_value) for c in "()/\.-?*"):
            for pos in pos_list:
                if pos_value.upper() == pos.upper():
                    value = pos
                    continue

            if pos_value in pos_map.keys():
                value = pos_map[pos_value]
            elif extra_pos_map and pos_value in extra_pos_map.keys():
                value = extra_pos_map[pos_value]

            if value is None:
                if pos_value not in self._missing_pos_list:
                    self._missing_pos_list.append(pos_value)

        return value

    def _validate_gloss(self, gloss_value, extra_gloss_map=None):
        """
        This function validates the gloss value
        in a gloss list from the TC gloss list.
        """

        gloss_list = ["AGR", "ST", "STR", "W", "CONS", "ANIM", "HUM", "INANIM", "ADD",
                      "ASP", "CESSIVE", "CMPL", "CON", "CONT", "CUST", "DUR", "DYN", "EGR",
                      "FREQ", "HAB", "INCEP", "INCH", "INCOMPL", "INGR", "INTS", "IPFV", "ITER",
                      "PFV", "PNCT", "PROG", "PRSTV", "REP", "RESLT", "SEMF", "STAT", "NCOMPL",
                      "PRF", "FV", "IV", "ABES", "ABL", "ABS", "ACC", "ADES", "ALL", "BEN",
                      "case marker - underspecified", "COMIT", "CONTL", "DAT", "DEL", "DEST",
                      "ELAT", "EQT", "ERG", "ESS", "GEN", "ILL", "INESS", "INSTR", "LAT", "MALF",
                      "NOM", "OBL", "PERL", "POSS", "PRTV", "TER", "VIAL", "VOC", "ORN", "CLITcomp",
                      "CLITadv", "CLITdet", "CLITn", "CLITp", "CLITpron", "CLITv", "ATV", "FAM", "INFOC",
                      "RFTL", "TPID", "UNID", "APPROX", "DIST", "DIST2", "DXS", "MEDIAL", "PROX", "AD",
                      "ADJ>ADV", "ADJ>N", "ADJ>V", "AUG", "DIM", "INCORP", "KIN", "N>ADJ", "N>ADV", "NMLZ",
                      "N>N", "NUM>N", "N>V", "PTCP>ADJ", "QUAL", "V>ADJ", "V>ADV", "vbl", ">Vitr", "V>N",
                      ">Vtr", "V>Nagt", "V>Ninstr", "ACAUS", "APASS", "APPL", "CAUS", "PASS", "ASRT",
                      "DECL", "EXCL", "IMP", "IMP1", "IMP2", "IND", "INTR", "MAVM", "PROH", "Q", "RPS",
                      "COMM", "FEM", "MASC", "NEUT", "COMPL", "DO", "ICV", "OBJ", "OBJ2", "objcogn", "OBJind",
                      "OM", "SBJ", "SC", "SM", "AFFMT", "CNTV", "COND", "CONJ", "CONTP", "EVID", "IRR", "JUSS",
                      "MOD", "OPT", "RLS", "SBJV", "OBLIG", "POT", "MNR", "MO", "CL", "CL1", "CL10", "CL11",
                      "CL12", "CL13", "CL14", "CL15", "CL16", "CL17", "CL18", "CL2", "CL20", "CL21", "CL22",
                      "CL23", "CL3", "CL4", "CL5", "CL6", "CL7", "CL8", "CL9", "Npref", "landmark", "DU",
                      "PL", "SG", "x", "DISTRIB", "1excl", "1incl", "1PL", "1SG", "2PL", "2SG",
                      "3B", "3PL", "3Pobv", "3Pprox", "3SG", "3Y", "4", "AREAL", "PLassc", "FT", "H", "!H",
                      "L", "MT", "RT", "NEGPOL", "POSPOL", "DEF", "INDEF", "SGbare", "SPECF", "PART", "2HML", "2HON",
                      "HON", "TTL", "AGT", "EXP", "GOAL", "PSSEE", "PSSOR", "PT", "SRC", "TH", "CIRCM", "CTed", "DIR",
                      "ENDPNT", "EXT", "INT", "LINE", "LOC", "PATH", "PRL", "SPTL", "STARTPNT", "VIAPNT", "DM", "MU",
                      "PS", "ANT", "AOR", "AUX", "FUT", "FUTclose", "FUTim", "FUTnear", "FUTrel", "FUTrm", "NF", "NFUT",
                      "NPAST", "PAST", "PASThst", "PASTim", "PASTpast", "PASTrel", "PASTrm", "PRES", "PRET", "FOC",
                      "TOP", "CNJ", "CLF", "CV", "GER", "GERDV", "INF", "itr", "PRED", "PTCP", "SUPN", "Vstem", "ACTV",
                      "?", "ABB", "ABSTR", "ADJstem", "ADV>ADJ", "ASS", "ASSOC", "ATT", "CMPR", "CO-EV", "CONSEC",
                      "CONTR", "COP", "DEG", "DEM", "DIR-SP", "EMPH", "EXPLET", "GNR", "IND-SP", "K1", "K2", "LOCREL",
                      "NEG", "Nstem", "oBEN", "PPOSTstem", "PRIV", "QUOT", "RECP", "REDP", "REFL", "REL", "RP-SP",
                      "sBEN", "SLCT", "SUP"]

        gloss_map = {"1": "CL1", "2": "CL2", "3": "CL3", "5": "CL5", "6": "CL6", "7": "CL7",
                     "8": "CL8", "9": "CL9", "14": "CL14", "15": "CL15", "16": "CL16",
                     "17": "CL17", "18": "CL18", "NPST": "NPAST", "EMP": "EMPH", "EXCLAM": "EXCL",
                     "COM": "COMIT", "PERF": "PFV", "CLAS": "CLF", "REF": "REFL", "?IPFV": "IPFV"}

        valid_glosses = []
        splitter = "."

        # split gloss values
        if "?" in gloss_value and gloss_value != "?IPFV":
            return None

        if ":" in gloss_value:
            splitter = ":"

        for gl in gloss_value.split(splitter):
            for gloss in gloss_list:
                if gl.upper() == gloss.upper():
                    valid_glosses.append(gloss)

            if gl in gloss_map.keys():
                valid_glosses.append(gloss_map[gl])
            elif extra_gloss_map and gl in extra_gloss_map:
                valid_glosses.append(extra_gloss_map[gl])

        if valid_glosses:
            return valid_glosses
        else:
            if gloss_value.isupper():
                if gloss_value not in self._missing_gloss_list:
                    self._missing_gloss_list.append(gloss_value)

            return None