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

import os
import re
import codecs

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


    def elan_to_graf(self):

        graph = Graph()

        parser = XmlContentHandler(self.filename)
        parser.parse()

        tier_counter = 0

        for element in parser.elan_map:

            # Common to all the nodes
            node_attributes = element[1]

            add_annotation_space = False

            if element[0] == 'TIER':

                node_id = "tier-n"+str(tier_counter)
                node = Node(node_id)

                # Annotation
                ann_name = 'tier'
                ann_id = "tier-"+str(tier_counter)
                annotation = Annotation(ann_name, None, ann_id)

                for attributes in element[1]:
                    attribute = attributes.split(' - ')
                    feature = attribute[0]
                    value = attribute[1]
                    annotation.features[feature] = value

                node.annotations.add(annotation)
                graph.nodes.add(node)

                annotation_space = AnnotationSpace(ann_name)
                annotation_space.add(annotation)

                graph.annotation_spaces.add(annotation_space)

                from_node = node

                tier_id = [x for x in node_attributes if
                           'TIER_ID - ' in x][0].split(' - ')[1]
                linguistic_type_ref = [x for x in node_attributes
                                       if 'LINGUISTIC_TYPE_REF - ' in
                                          x][0].split(' - ')[1]

                tier_counter+=1

            if element[0] == 'ALIGNABLE_ANNOTATION':
                # Anchors for the regions
                anchors = node_attributes
                anchor_1 = anchors[1].split(' - ')
                anchor_1 = parser.time_slot_dict[anchor_1[1]]
                anchor_2 = anchors[0].split(' - ')
                anchor_2 = parser.time_slot_dict[anchor_2[1]]
                anchors = [anchor_1, anchor_2]

                # Annotation
                ann_name = linguistic_type_ref
                ann_id = node_attributes[2].split(' - ')[1]
                annotation_value = element[3].split(' - ')[1]
                annotation = Annotation(ann_name, None, ann_id)
                annotation.features['annotation_value'] = annotation_value

                index = re.sub("\D", "", ann_id)

                node_id = tier_id+"-n"+index
                node = Node(node_id)

                region_id = tier_id+"-r"+index
                region = Region(region_id, *anchors)

                edge_id = element[0]+"-e"+index
                edge = Edge(edge_id, from_node, node)

                node.annotations.add(annotation)
                node.add_region(region)

                depends = element[2].split(' - ')[1]

                if not depends in graph.header.depends_on:
                    graph.header.add_dependency(depends)

                graph.regions.add(region)
                graph.edges.add(edge)
                graph.nodes.add(node)

                add_annotation_space = True

            if element[0] == 'REF_ANNOTATION':
                # Annotation
                ann_name = linguistic_type_ref
                ann_id = node_attributes[1].split(' - ')[1]
                annotation_value = element[3].split(' - ')[1]
                annotation = Annotation(ann_name, None, ann_id)
                annotation.features['annotation_value'] = annotation_value

                index = re.sub("\D", "", ann_id)

                node_id = tier_id+"-n"+index
                node = Node(node_id)

                node.annotations.add(annotation)
                graph.nodes.add(node)

                add_annotation_space = True

            if add_annotation_space:
                annotation_space = AnnotationSpace(linguistic_type_ref)
                annotation_space.add(annotation)

                graph.annotation_spaces.add(annotation_space)

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