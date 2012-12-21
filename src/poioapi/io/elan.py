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

from poioapi.io import header
from poioapi.io.analyzer import XmlContentHandler

from graf import Graph, GrafRenderer
from graf import Node, Edge
from graf import Annotation, AnnotationSpace
from graf import Region

class ElanToGraf:
    """
    Class that will handle elan files.

    """

    def __init__(self, filepath):
        self.filename = os.path.basename(filepath)
        self.filepath = filepath
        (self.basedirname, _) = os.path.splitext(os.path.abspath(self.filepath))

        # Create the header file
        self.header = header.CreateHeaderFile(self.basedirname)

    def elan_to_graf(self):

        graph = Graph()

        parser = XmlContentHandler(self.filepath)
        parser.parse()

        tier_counter = 0

        data_structure_basic = []
        constraints = dict()

        # Mandatory to give an author to the file
        self.header.author = 'CIDLeS'
        self.header.filename = self.filename.split('.eaf')[0]
        self.header.primaryfile = self.filename

        for element in parser.elan_list:

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

                tier_counter+=1

                tier_id = [x for x in node_attributes if
                           'TIER_ID - ' in x][0].split(' - ')[1]

                linguistic_type_ref = [x for x in node_attributes
                                       if 'LINGUISTIC_TYPE_REF - ' in
                                          x][0].split(' - ')[1]

                try:
                    parent_ref = [x for x in node_attributes
                                           if 'PARENT_REF - ' in
                                              x][0].split(' - ')[1]
                except IndexError as indexError:
                    parent_ref = None

                if not tier_id in data_structure_basic:
                    data_structure_basic.append((tier_id, parent_ref))

                if not tier_id in self.header.annotation_list:
                    self.header.add_annotation(self.filename, tier_id)
                    self.header.add_annotation_attributes(tier_id,
                        'tier', node_attributes)
                    for linguistic_type in parser.linguistic_type_list:
                        linguistic_type_id = [x for x in linguistic_type
                                              if 'LINGUISTIC_TYPE_ID - ' in
                                                 x][0].split(' - ')[1]

                        if linguistic_type_ref == linguistic_type_id:
                            self.header.add_annotation_attributes(tier_id,
                                'linguistic_type', linguistic_type)
                            break

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

        # Close the header file
        self.header.create_header()

        data_final = []
        data_hierarchy_dict = dict()

        # Mapping the tiers with the parent
        # references (Dependencies)
        for strc_elements in data_structure_basic:
            tier = strc_elements[0]
            empty_parents = True
            child_list = []
            for parents in data_structure_basic:
                parent = parents[1]
                if tier == parent:
                    child_list.append(parents[0])
                    empty_parents = False

            if empty_parents:
                data_hierarchy_dict[tier] = None
            else:
                data_hierarchy_dict[tier] = child_list

        for dict_elements in data_hierarchy_dict.items():
            print(dict_elements)

        # Creating the final data_structure_hierarchy
        for strc_elements in data_structure_basic:
            tier = strc_elements[0]
            for dict_elements in data_hierarchy_dict.items():
                key = dict_elements[0]
                elements = dict_elements[1]
                if key == tier:
                    if elements is None:
                        data_final.append(key)
                    else:
                        data_final.append([key, elements])

        print(data_final)

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


