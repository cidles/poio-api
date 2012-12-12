# -*- coding: utf-8 -*-
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
"""This module contains classes to access Elan data.

The class Eaf is a low level API to .eaf files.

EafGlossTree, EafPosTree, etc. are the classes to access the data via
tree, which also contains the original .eaf IDs. Because of this
EafTrees are read-/writeable.
"""
import codecs

import os

from xml.dom import minidom

from poioapi.io.analyzer import XmlContentHandler
from graf.io import Graph, GrafRenderer
from graf.graphs import Node, Edge
from graf.annotations import Annotation, AnnotationSpace
from graf.media import Region

class ElanToGraf:
    """
    Class that will handle elan files.

    """

    def __init__(self, filename):
        self.filename = filename
        self.counter = 0
        self.tier_counter = 0

    def elan_to_graf(self):

        graph = Graph()

        parser = XmlContentHandler(self.filename)
        parser.parse()

        for element in parser.elan_map:

            if element[0] == 'TIER':
                node_id = element[0]+"-n"+str(self.tier_counter)
                node = Node(node_id)

                # Annotation
                ann_name = element[0]
                ann_id = ann_name+"-"+str(self.tier_counter)
                annotation = Annotation(ann_name, None, ann_id)

                for attributes in element[1]:
                    attribute = attributes.split(' - ')
                    feature = attribute[0]
                    value = attribute[1]
                    annotation.features[feature] = value

                node.annotations.add(annotation)
                graph.nodes.add(node)

                ann_name_id = element[0]

                annotation_space = AnnotationSpace(ann_name)
                annotation_space.add(annotation)

                graph.annotation_spaces.add(annotation_space)

                from_node = node

                self.tier_counter+=1

            if element[0] == 'ALIGNABLE_ANNOTATION':
                anchors = element[1]
                anchor_1 = anchors[1].split(' - ')
                anchor_1 = parser.time_slot_dict[anchor_1[1]]
                anchor_2 = anchors[0].split(' - ')
                anchor_2 = parser.time_slot_dict[anchor_2[1]]
                anchors = [anchor_1, anchor_2]

                node_id = element[0]+"-n"+str(self.counter)
                node = Node(node_id)

                region_id = element[0]+"-r"+str(self.counter)
                region = Region(region_id, *anchors)

                edge_id = element[0]+"-e"+str(self.counter)
                edge = Edge(edge_id, from_node, node)

                # Annotation
                ann_name = element[0]
                ann_id = element[1]
                ann_id = ann_id[2].split(' - ')
                annotation_value = element[3].split(' - ')
                annotation = Annotation(ann_name, None, ann_name+"-"+ann_id[1])
                annotation.features['string'] = annotation_value[1]

                node.annotations.add(annotation)
                node.add_region(region)

                depends = element[2].split(' - ')

                if not depends[1] in graph.header.depends_on:
                    graph.header.add_dependency(depends[1])

                graph.regions.add(region)
                graph.edges.add(edge)
                graph.nodes.add(node)

                ann_name_id = element[0]

                annotation_space = AnnotationSpace(ann_name_id)
                annotation_space.add(annotation)

                graph.annotation_spaces.add(annotation_space)

                self.counter+=1

            if element[0] == 'REF_ANNOTATION':
                # Annotation
                ann_name = element[0]
                ann_id = element[1]
                ann_id = ann_id[1].split(' - ')
                annotation_value = element[3].split(' - ')
                annotation = Annotation(ann_name, None, ann_name+"-"+ann_id[1])
                annotation.features['string'] = annotation_value[1]

                from_node.annotations.add(annotation)

                depends = element[2].split(' - ')

                if not depends[1] in graph.header.depends_on:
                    graph.header.add_dependency(depends[1])

                ann_name_id = element[0]

                annotation_space = AnnotationSpace(ann_name_id)
                annotation_space.add(annotation)

                graph.annotation_spaces.add(annotation_space)

                self.counter+=1

        return graph

    def graf_render(self, outputfile, graph):

        graf_render = GrafRenderer(outputfile+"_tmp")
        graf_render.render(graph)

        # Indent the Xml file
        file = codecs.open(outputfile,'w','utf-8')
        xml = minidom.parse(outputfile+"_tmp")
        file.write(xml.toprettyxml(' '))
        file.close()

        # Delete the temp file
        os.remove(outputfile+"_tmp")


file = '/home/alopes/tests/elan/example.eaf'
elan_graf = ElanToGraf(file)

graph = elan_graf.elan_to_graf()

# Just to see the result faster
outputfile = '/home/alopes/tests/elan/example_render.xml'
elan_graf.graf_render(outputfile, graph)