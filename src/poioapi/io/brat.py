# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

"""

"""

from __future__ import unicode_literals

import os


class Writer():
    def __init__(self, graf, outputfile):
        self.outputfile = outputfile
        self.graf = graf

    def write(self, annotation_space, feature_name="annotation_value"):
        ann_file = open(self.outputfile+".ann", "w")
        t = 1
        n = 1
        relation_map = {}

        label_list = ["head", "translation", "pos", "italic", "bold"]

        for annotation in self.graf.annotation_spaces[annotation_space]:
            if annotation.label in label_list:
                if feature_name in annotation.features:
                    annotation_value = annotation.features[feature_name]

                    if annotation_value:
                        node = annotation.element

                        for feature, value in annotation.features.items():
                            if value:
                                if feature != feature_name:
                                    annotation_type = value
                                else:
                                    annotation_type = annotation.label

                                if node.links:
                                    anchors = node.links[0][0].anchors
                                    line = "T{0}\t{1} {2} {3}\t{4}\n".\
                                        format(t, annotation_type, anchors[0], anchors[1], annotation_value)
                                    note = "#{0}\tAnnotatorNotes T{1}\t{2}\n".format(n, t, node)
                                    relation_map[node.id] = "T{0}".format(t)

                                    ann_file.write(line)
                                    ann_file.write(note)
                                    t += 1
                                    n += 1

        ann_file.close()

    def create_relations(self, relation_map, ann_file):
        r = 1

        for node_id, text_bound in relation_map.items():
            for edge in self.graf.edges:
                if node_id == edge.from_node.id:
                    line = "R{0}	To Arg1:{2} Arg2:{1}\n".\
                        format(r, relation_map[edge.from_node.id],
                               relation_map[edge.to_node.id])
                    r += 1
                    ann_file.write(line)

        return ann_file

    def create_conf_file(self):
        basedirname = os.path.dirname(self.outputfile)

        annotation_conf = open(basedirname+"/annotation.conf", "w")

        annotation_conf.write("[entities]\n")

        for entity in self.graf.header.annotation_spaces:
            annotation_conf.write(entity+"\n")

        annotation_conf.write("\n[relations]\n# To Arg1:<ENTITY>, Arg2:<ENTITY>"
                              "\n<OVERLAP>	Arg1:<ENTITY>, Arg2:<ENTITY>, <OVL-TYPE>:<ANY>"
                              "\n\n[events]\n# none\n\n[attributes]\n# none")

        annotation_conf.close()