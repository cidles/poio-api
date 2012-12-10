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

from xml.dom import minidom

from poioapi.io.analyzer import XmlContentHandler
from graf.io import Graph, GrafRenderer, GraphParser
from graf.graphs import Node, Link
from graf.annotations import AnnotationSpace, Annotation, FeatureStructure
from graf.media import Region

file = 'C:\\tests\elan\example.eaf'
content = XmlContentHandler(file)
content.parse()

graph = Graph()
counter = 0

for value in content.elan_map:
    # There's no need to add the link because the region do it by itself
    # Firts with the time slots (something like the utterances)
    if counter < 5:
        if value[0] == 'ALIGNABLE_ANNOTATION':
            print(value)
            anchors = value[1]
            anchor_1 = anchors[1].split(' - ')
            anchor_1 = content.time_slot_dict[anchor_1[1]]
            anchor_2 = anchors[0].split(' - ')
            anchor_2 = content.time_slot_dict[anchor_2[1]]
            node = Node(value[0]+"-n"+str(counter))
            anchors = [anchor_1, anchor_2]
            id = value[0]+"-r"+str(counter)
            region = Region(id, *anchors)
            # In the end adding a region to a node is create a
            # link to a real region in the graf
            node.add_region(region)
            feature_strct = FeatureStructure() # Structure
            feature_strct['feature1'] = 'value_1'
            feature_strct['feature2'] = 'value_2'
            annotation = Annotation('label', feature_strct)
            annotation.features['another_feature'] = 'value_another'
            annotation.features['feature3'] = 'value_3'
            node.annotations.add(annotation)

            as_id = 'as_id'
            aspace = graph.annotation_spaces.create(as_id)

            graph.regions.add(region)
            graph.nodes.add(node)
            counter+=1

#graf_render = GrafRenderer('C:\\tests\ddd.xml')
#graf_render.render(graph)


file = open(file, 'w')
xml = minidom.parse(file)
file.write(xml.toprettyxml(' '))
file.close()
