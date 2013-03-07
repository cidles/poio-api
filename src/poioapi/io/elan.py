# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

"""This module contains classes to access Elan data.
The class Eaf is a low level API to .eaf files.

EafGlossTree, EafPosTree, etc. are the classes to
access the data via tree, which also contains the
original .eaf IDs. Because of this EafTrees are
read-/writeable.
"""

from __future__ import absolute_import
from collections import defaultdict

import os
import re

from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.etree.ElementTree as ET

from graf.annotations import FeatureStructure

from poioapi.io.graf import Writer, BaseParser

from graf import Graph
from graf import Node, Edge
from graf import Annotation, AnnotationSpace
from graf import Region

class Parser(BaseParser):
    """
    Class that will handle parse Elan files.

    """

    def __init__(self, filepath, data_structure_hierarchy=None):
        """Class's constructor.

        Parameters
        ----------
        filepath : str
            Path of the elan file.
        data_structure_hierarchy : object
            This object contains the data hierarchy and the constraints.

        """

        self.filename = os.path.basename(filepath)
        self.filepath = filepath
        (self.basedirname, _) = os.path.splitext(os.path.abspath(self.filepath))

        if data_structure_hierarchy is not None:
            self.data_structure_hierarchy = data_structure_hierarchy
        else:
            self.data_structure_hierarchy = []

        self.data_structure_constraints = dict()
        self.data_hierarchy_parent_dict = dict()

        self.xml_files_map = {}

        self.graf = Writer()

    def as_graf(self):
        self.graph = Graph()

        self.tree = ET.parse(self.filepath).getroot()

        self.regions_map = self._get_regions()

        self.tiers = self.tree.findall('TIER')
        root_tiers = self.get_root_tiers(self.tiers)

        for root_tier in root_tiers:
            self._parent_tier_id = None
            self._parent_linguistic_type_ref = None

            self._tier_id = root_tier.attrib['TIER_ID']
            self._linguistic_type_ref = root_tier.attrib['LINGUISTIC_TYPE_REF'].\
            replace(" ","_")

            root_annotations = self.get_annotations_for_tier(root_tier)
            self.add_graf_annotations(root_annotations)

            self.find_children_tiers_for_tier(root_tier)

        return self.graph

    def get_root_tiers(self, tiers=None):

        root_tiers = []

        for tier in tiers:
            if not 'PARENT_REF' in tier.attrib:
                root_tiers.append(tier)

        return root_tiers

    def get_child_tiers_for_tier(self, tier):

        tier_id = tier.attrib['TIER_ID']

        tier_childs = self.tree.findall("TIER[@PARENT_REF='"+tier_id+"']")

        return tier_childs

    def find_children_tiers_for_tier(self, tier):

        children = self.get_child_tiers_for_tier(tier)

        for child in children:
            annotations = self.get_annotations_for_tier(child)

            self._parent_tier_id = tier.attrib['TIER_ID']
            self._parent_linguistic_type_ref = tier.attrib['LINGUISTIC_TYPE_REF'].\
            replace(" ","_")

            self._tier_id = child.attrib['TIER_ID']
            self._linguistic_type_ref = child.attrib['LINGUISTIC_TYPE_REF'].\
            replace(" ","_")

            self.add_graf_annotations(annotations)

            child_children = self.get_child_tiers_for_tier(child)

            if len(child_children) > 0:
                self.find_children_tiers_for_tier(child)

    def get_annotations_for_tier(self, tier, annotation_parent=None):

        tier_annotations = tier.findall("ANNOTATION")

        return tier_annotations

    def add_graf_annotations(self, annotations):

        prefix_name = self._linguistic_type_ref+"/"+self._tier_id
        annotation_name = self._linguistic_type_ref
        parent_ref = self._parent_linguistic_type_ref

        for annotation in annotations:
            annotation_elements = annotation.getiterator()

            if annotation_elements[1].tag == 'ALIGNABLE_ANNOTATION':
                annotation_id = annotation_elements[1].attrib['ANNOTATION_ID']
                annotation_value = annotation_elements[1].find('ANNOTATION_VALUE').text

                features_map = {'annotation_value':annotation_value,
                                'time_slot1':annotation_elements[1].attrib['TIME_SLOT_REF1'],
                                'time_slot2':annotation_elements[1].attrib['TIME_SLOT_REF2']}

                regions = (self.regions_map[annotation_elements[1].attrib['TIME_SLOT_REF1']],
                           self.regions_map[annotation_elements[1].attrib['TIME_SLOT_REF2']])

                index = re.sub("\D", "", annotation_id)

                if parent_ref is not None:
                    from_node = self.find_from_node(parent_ref, regions)
                else:
                    from_node = None

                self.add_graf_node(index, prefix_name, regions, from_node)

                annotation_ref = prefix_name+"/n"+index

                self.add_graf_annotation(annotation_name, annotation_id,
                    annotation_ref, features_map)
            else:
                annotation_id = annotation_elements[1].attrib['ANNOTATION_ID']
                annotation_value = annotation_elements[1].find('ANNOTATION_VALUE').text
                annotation_ref = annotation_elements[1].attrib['ANNOTATION_REF']

                features_map = {'annotation_value':annotation_value,
                                'ref_annotation':annotation_ref,
                                'tier_id':self._tier_id}

                for attribute in annotation_elements[1].attrib:
                    if attribute != 'ANNOTATION_REF' and\
                       attribute != 'ANNOTATION_ID' and\
                       attribute != 'ANNOTATION_VALUE':
                        features_map[attribute] = annotation_elements[1].attrib[attribute]

                index = re.sub("\D", "", annotation_ref)

                annotation_ref = self._parent_linguistic_type_ref+"/"+\
                                 self._parent_tier_id+"/n"+index

                self.add_graf_annotation(annotation_name, annotation_id,
                    annotation_ref, features_map)

    def find_from_node(self, parent_ref, anchors):
        for region in self.graph.regions:
            if parent_ref in region.id:
                if (int(region.anchors[0]) <= int(anchors[0]) <= int(region.anchors[1]))\
                and (int(region.anchors[0]) <= int(anchors[1]) <= int(region.anchors[1])):
                    node_id = re.sub(r"(.*)/r", r"\1/n", region.id)
                    node = self.graph.nodes[node_id]
                    return node
        return None

    def _get_regions(self):
        time_order = self.tree.find('TIME_ORDER')
        time_order_dict = dict()

        for time in time_order:
            key = time.attrib['TIME_SLOT_ID']

            if 'TIME_VALUE' in time.attrib:
                value = time.attrib['TIME_VALUE']
            else:
                value = 0

            time_order_dict[key] = value

        return time_order_dict

    def add_graf_node(self, node_index, prefix_name, regions=None, from_node=None):

        node_id = prefix_name+"/n"+node_index
        node = Node(node_id)

        if from_node is not None:
            edge_id = "e"+node_index
            edge = Edge(edge_id, from_node, node)

            self.graph.edges.add(edge)

        if regions is not None:
            region_id = prefix_name+"/r"+node_index
            region = Region(region_id, *regions)
            node.add_region(region)

            self.graph.regions.add(region)

        self.graph.nodes.add(node)

    def add_graf_annotation(self, annotation_name, annotation_id,
                            annotation_ref, annotation_features=None):

        annotation = Annotation(annotation_name, annotation_features,
            annotation_id)

        self.graph.nodes[annotation_ref].annotations.add(annotation)

        annotation_space = AnnotationSpace(annotation_name)
        annotation_space.add(annotation)

        self.graph.annotation_spaces.add(annotation_space)

    def tier_has_regions(self, tier):
        pass

    def annotation_has_regions(self, annotation):
        pass