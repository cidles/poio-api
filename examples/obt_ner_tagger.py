# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: Peter Bouda <pbouda@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

from __future__ import unicode_literals

import sys
import os
import codecs
import re
import glob
import subprocess
import itertools
import io
import collections
import tempfile

import poioapi.annotationgraph
import poioapi.data
import poioapi.io.graf

import graf

############################################## Typecraft mapping

# OBT unclear: fork, ukjent

# what to do with "verb perf-part"? Is it a "verb" or a "participle" in
# Typcraft?

pos_1 = collections.OrderedDict({
    "adj" : "ADJ",
    "adv" : "ADV",
    "det" : "DET",
    "inf-merke" : "PRtinf",
    "interj" : "INTRJCT",
    "konj" : "CONJ",
    "prep" : "P",
    "pron" : "PN",
    "subst" : "N",
    "sbu" : "CONJS",
    "verb" : "V"
})

pos_2 = collections.OrderedDict({
    ("adj", "sup") : "ADJS",
    ("adj", "komp") : "ADJC",
    ("pron", "poss") : "PNposs",
    ("pron", "refl") : "PNrefl",
    ("subst", "prop") : "Np",
    ("subst", "fem") : "NFEM",
    ("subst", "mask") : "NMASC",
    ("subst", "nøyt") : "NNEUT",
    ("subst", "ub") : "Ncomm"
})

def map_pos(node_tags):
    tc_pos = ""

    for k in pos_2:
        if set(k) < set(node_tags):
            tc_pos = pos_2[k]
            break

    if tc_pos == "":
        for k in pos_1:
            if k in node_tags:
                tc_pos = pos_1[k]
                break

    return tc_pos

def add_pos_node(graf_graph, node, pos, last_used_id):
    node_id = "pos_typecraft..na{0}".format(last_used_id)
    pos_node = graf.Node(node_id)
    ann = graf.Annotation("pos_typecraft",
        {"annotation_value": pos}, "a{0}".format(last_used_id))
    pos_node.annotations.add(ann)
    graf_graph.nodes.add(pos_node)
    graf_graph.create_edge(node, pos_node)
    return last_used_id + 1

def word_as_typecraft(ag, word, pos_in_phrase):
    XML = """<word head="false" text="{word}" pos_in_phrase="{pos_in_phrase}">
            <pos>{pos}</pos>
            <morpheme meaning="" baseform="" text="{word}"/>
        </word>
        """

    word_str = ag.annotation_value_for_node(word)
    poses = list()
    for pos in ag.nodes_for_tier("pos_typecraft", word):
        poses.append(ag.annotation_value_for_node(pos))

    pos_str = ""
    if len(poses) > 0:
        pos_str = poses[0]

    return XML.format(word=word_str, pos_in_phrase=pos_in_phrase, pos=pos_str)

def ne_as_typecraft(ag, phrase):
    XML = """<namedEntities>
{nes}        </namedEntities>"""

    XML_NE = """            <entity class="{ne_type}" tokenIDs="{word_ids}"/>
"""

    nes = collections.defaultdict(list)
    for pos_in_phrase, word in enumerate(ag.nodes_for_tier("word", phrase)):
        for ne in ag.nodes_for_tier("named_entity", word):
            nes[ne].append("{0}".format(pos_in_phrase))

    if len(nes) == 0:
        return ""

    ne_xml = ""
    for ne in nes:
        word_ids = " ".join(nes[ne])
        ne_type = ag.annotation_value_for_node(ne)
        ne_xml += XML_NE.format(ne_type=ne_type, word_ids=word_ids)

    return XML.format(nes=ne_xml)

def phrase_as_typecraft(ag, phrase):
    XML = """<phrase valid="VALID" id="">
        <original>{phrase}</original>
        <translation></translation>
        <description></description>
        <globaltags tagset="Default" id="1"/>
        {words}
        {nes}
    </phrase>
    """

    words_xml = ""
    words = list()
    for i, word in enumerate(ag.nodes_for_tier("word", phrase)):
        words.append(ag.annotation_value_for_node(word))
        words_xml += word_as_typecraft(ag, word, i)

    nes_xml = ne_as_typecraft(ag, phrase)
    # create the phrase string
    phrase_str = " ".join(words)
    phrase_str = re.sub(" (?=[.,;!?])", "", phrase_str)
    phrase_xml = XML.format(phrase=phrase_str, words=words_xml,
        nes=nes_xml)

    return phrase_xml

def ag_as_typecraft(ag):
    XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<typecraft xsi:schemaLocation="http://typecraft.org/typecraft.xsd" xmlns="http://typecraft.org/typecraft" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
{phrases}
</typcraft>"""

    phrases_xml = ""
    for phrase in ag.root_nodes():
        phrases_xml += phrase_as_typecraft(ag, phrase)

    return XML.format(phrases=phrases_xml)

############################################## Helpers

obt_tagger_command = \
    "/Users/pbouda/Projects/git-github/The-Oslo-Bergen-Tagger/tag-nostat-bm.sh"

ner_tag_for_type = {
    "by_navn" : "city",
    "etternavn" : "family_name",
    "fylkesnavn" : "county",
    "guttenavn" : "boy_name",
    "jentenavn" : "girl_name",
    "kommune_navn" : "district",
    "land_navn" : "country"
}

re_ner_type = re.compile("([^.]*)\.txt$")

def parse_ner_list(filename):
    mwes = set()
    with codecs.open(filename, "r", "utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("[ STEM <"):
                words = line[9:-3]
                if words.startswith('"'):
                    words = words[1:-1]
                words = re.split('", "', words)
                words = [w.lower() for w in words if w.lower() not in \
                    ['de', 'den', 'det']]
                mwes.add(tuple(words))
    return mwes

def obt_tagger(inputfile):
    # pre-process file: OBT crashes when there are three newlines
    with codecs.open(inputfile, "r", "utf-8") as f:
        content = f.read()
    re_newlines = re.compile("[\n]+", re.MULTILINE)
    content = re_newlines.sub("\n", content)

    out = ""
    with tempfile.NamedTemporaryFile() as temp:
        temp.write(content.encode("utf-8"))
        temp.flush()
        proc = subprocess.Popen([obt_tagger_command, temp.name],
            cwd=os.path.dirname(obt_tagger_command), stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        (out, _) = proc.communicate()
    return out.decode("utf-8")

def last_used_id_in_graf(graf):
    last_used_id = 0
    for n in graf.nodes:
        n_id = int(re.search("\d+$",n.id).group(0))
        if n_id > last_used_id:
            last_used_id = n_id
    return last_used_id

def add_ner_node(graf_graph, parent_nodes, ner_tag, last_used_id):
    node_id = "named_entity..na{0}".format(last_used_id)
    ner_node = graf.Node(node_id)
    ann = graf.Annotation("named_entity",
        {"annotation_value": ner_tag}, "a{0}".format(last_used_id))
    ner_node.annotations.add(ann)
    graf_graph.nodes.add(ner_node)
    for n in parent_nodes:
        graf_graph.create_edge(n, ner_node)
    return last_used_id + 1

def tags_for_tuple(ner_dict, variant_tuple):
    tags = set()
    for ner_tag in ner_dict:
        if variant_tuple in ner_dict[ner_tag]:
            tags.add(ner_tag)
    return tags

def node_ngrams_for_tier(ag, tier, parent, ngram_size):
    current_ngram = list()
    ngrams = list()
    nodes = ag.nodes_for_tier(tier, parent)

    for i in range(ngram_size - 1):
        if i >= len(nodes):
            break
        current_ngram.append(nodes[i])

    i = ngram_size - 1
    while i < len(nodes):
        current_ngram.append(nodes[i])
        ngrams.append(list(current_ngram))
        current_ngram.pop(0)
        i += 1

    return ngrams

######################################################### Main

def main(argv):
    if len(argv) != 3:
        print("Usage: obt_ner_tagger.py inputfile outputfile")
        sys.exit(1)

    inputfile = os.path.realpath(argv[1])
    outputfile = os.path.realpath(argv[2])
    scriptpath = os.path.dirname(os.path.realpath(__file__))
    
    ner_dict = dict()

    for ner_file in glob.glob(os.path.join(scriptpath, "ner_lists", "*.txt")):
        ner_type = re_ner_type.search(ner_file).group(1)
        ner_set = parse_ner_list(ner_file)
        ner_dict[ner_tag_for_type[ner_type]] = ner_set

    # find out what the longest MWE is
    max_ngram = 0
    for ner_tag in ner_dict:
        for mwe in ner_dict[ner_tag]:
            if len(mwe) > max_ngram:
                max_ngram = len(mwe)

    # get the OBT tagger output
    obt_out = obt_tagger(inputfile)
    # Create an empty annotation graph
    ag = poioapi.annotationgraph.AnnotationGraph.from_obt(io.StringIO(obt_out))
    #hierarchy = ag.tier_hierarchies[0]
    #hierarchy[1].append('named_entity') 
    #ag.structure_type_handler = poioapi.data.DataStructureType(hierarchy)
    last_used_id = last_used_id_in_graf(ag.graf)

    pos_dict = dict()

    for phrase in ag.root_nodes():
        # tag multi-word expressions (MWE) by comparing to lists only
        # does not depend on any OBT tags, as OBT does not support MWEs
        for ngram_size in range(2, max_ngram+1):
            ngrams = node_ngrams_for_tier(ag, "word", phrase, ngram_size)
            for ngram in ngrams:
                mwe_words = list()
                # collect all the variants
                for word in ngram:
                    variants = set()
                    variants.add(ag.annotation_value_for_node(word).lower())
                    for variant in ag.nodes_for_tier("variant", word):
                        variants.add(
                            ag.annotation_value_for_node(variant).lower())
                    mwe_words.append(variants)

                # get any tags for this MWE
                tags = set()
                # check if this is a MWE
                for variant in itertools.product(*mwe_words):
                    tags = tags.union(tags_for_tuple(ner_dict, tuple(variant)))

                # add tags to GrAF
                for t in tags:
                    last_used_id = add_ner_node(ag.graf, ngram, t, last_used_id)

        # now find tags for single words based on "prop" tags from OBT
        # also map POS from OBT to Typecraft
        for word in ag.nodes_for_tier("word", phrase):
            tags = set()
            is_prop = False
            variants = set()
            pos_found = False
            variants.add(ag.annotation_value_for_node(word).lower())
            for variant in ag.nodes_for_tier("variant", word):
                variants.add(ag.annotation_value_for_node(variant).lower())
                variant_tags = list()
                for tag in ag.nodes_for_tier("tag", variant):
                    # are we in a name?
                    t = ag.annotation_value_for_node(tag)
                    variant_tags.append(t)
                    if t == "prop":
                        is_prop = True

                # map POS
                tc_pos = map_pos(variant_tags)
                if tc_pos != "" and not pos_found:
                    last_used_id = add_pos_node(ag.graf, word, tc_pos,
                        last_used_id)
                    pos_found = True

            # was it a proper name?
            if is_prop:
                for variant in variants:
                    tags = tags.union(
                        tags_for_tuple(ner_dict, tuple([variant])))

            for t in tags:
                last_used_id = add_ner_node(ag.graf, [word], t, last_used_id)

            # if no tags were found than add default tag
            if len(tags) == 0 and is_prop:
                last_used_id = add_ner_node(ag.graf, [word], "proper",
                    last_used_id)

    xml_out = ag_as_typecraft(ag)
    with codecs.open(outputfile, "w", "utf-8") as f:
        f.write(xml_out)


if __name__ == "__main__":
    main(sys.argv)