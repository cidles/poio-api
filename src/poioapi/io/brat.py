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

import os


class Writer():
    def __init__(self, graf, outputfile):
        self.outputfile = outputfile
        self.graf = graf

    def write(self):
        ann_file = open(self.outputfile+".ann", "w")
        t = 1
        r = 1
        n = 1
        relation_map = {}

        for node in self.graf.nodes:
            annotation = node.annotations._elements[0]
            annotation_type = annotation.label

            if "annotation_value" in annotation.features:
                annotation_value = annotation.features["annotation_value"]
                if annotation_value is None:
                    continue
            else:
                continue

            if node.links:
                anchors = node.links[0][0].anchors
                line = "T{0}	{1} {2} {3}	{4}\n".\
                    format(t, annotation_type, anchors[0], anchors[1], annotation_value)
                note = "#{0}	AnnotatorNotes T{1}	{2}\n".format(n, t, node)
                relation_map[node.id] = "T{0}".format(t)

                ann_file.write(line)
                ann_file.write(note)
                t += 1
                n += 1

        for node_id, text_bound in relation_map.items():
            for edge in self.graf.edges:
                if node_id == edge.from_node.id:
                    line = "R{0}	To Arg1:{2} Arg2:{1}\n".\
                        format(r, relation_map[edge.from_node.id],
                               relation_map[edge.to_node.id])
                    r += 1
                    ann_file.write(line)

        ann_file.close()
        self.create_conf_file()

    def create_conf_file(self):
        basedirname = os.path.dirname(self.outputfile)

        annotation_conf = open(basedirname+"/annotation.conf", "w")

        annotation_conf.write("[entities]\n")

        for entity in self.graf.header.annotation_spaces:
            annotation_conf.write(entity+"\n")

        annotation_conf.write("\n[relations]\nTo Arg1:<ENTITY>, Arg2:<ENTITY>"
                              "\n\n[events]\n# none\n\n[attributes]\n# none")

        annotation_conf.close()