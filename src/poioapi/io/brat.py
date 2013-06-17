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
import re


class Writer():

    def __init__(self, graf):
        self.graf = graf

    def write(self, outputfile):
        lines = []
        fila = open(outputfile, "w", encoding="utf-8")

        for node in self.graf.nodes:
            annotation = node.annotations._elements[0]
            annotation_type = annotation.label

            if "annotation_value" in annotation.features:
                annotation_value = annotation.features["annotation_value"]
                if annotation_value is None:
                    continue
            else:
                continue

            # annotation_id = "T{0}".format(re.findall(r'\d+', node.id)[-1])
            annotation_id = "T{0}".format(node.id)

            if node.links:
                anchors = node.links[0][0].anchors

                line = "{0}	{1} {2} {3}	{4}\n".format(annotation_id, annotation_type,
                                                    anchors[0], anchors[1], annotation_value)

                fila.write(line)

        # for edge in self.graf.edges:
        #     relation_type = edge.annotations._elements[0].label
        #     relation_id = "R{0}".format(edge.id)
        #     # relation_id = "R{0}".format(re.findall(r'\d+', annotation.id)[-1])
        #     # arg1 = "T{0}".format(re.findall(r'\d+', edge.from_node.id)[-1])
        #     # arg2 = "T{0}".format(re.findall(r'\d+', edge.to_node.id)[-1])
        #     arg1 = "T{0}".format(edge.from_node.id)
        #     arg2 = "T{0}".format(edge.to_node.id)
        #     line = "{0}	{1} Arg1:{2} Arg2:{3}\n".format(relation_id, relation_type, arg1, arg2)
        #
        #     fila.write(line)

        fila.close()