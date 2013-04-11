# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

""" This document contain the responsible
methods to write and parse the GrAF files.
The parser use the ContentHandler from
SAX Xml module.
"""

from __future__ import absolute_import

import abc
import os

from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

import graf

import poioapi.io.header

class Tier:
    __slots__ = [ 'name', 'linguistic_type' ]

    def __init__(self, name, linguistic_type=None):
        self.name = name
        self.linguistic_type = linguistic_type

class Annotation:
    __slots__ = [ 'id', 'value', 'features' ]

    def __init__(self, id, value, features=None):
        self.value = value
        self.id = id
        self.features = features

class NodeId:
    __slots__ = [ 'prefix', 'index' ]

    def __init__(self, prefix, index):
        self.prefix = prefix
        self.index = index

    def __str__(self):
        return "{0}/n{1}".format(self.prefix, self.index)

    def str_edge(self):
        return "e{0}".format(self.index)

    def str_region(self):
        return "{0}/r{1}".format(self.prefix, self.index)

class BaseParser(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_root_tiers(self):
        raise NotImplementedError("Method must be implemented")

    @abc.abstractmethod
    def get_child_tiers_for_tier(self, tier):
        raise NotImplementedError("Method must be implemented")

    @abc.abstractmethod
    def get_annotations_for_tier(self, tier, annotation_parent=None):
        raise NotImplementedError("Method must be implemented")

    @abc.abstractmethod
    def tier_has_regions(self, tier):
        raise NotImplementedError("Method must be implemented")

    @abc.abstractmethod
    def region_for_annotation(self, annotation):
        raise NotImplementedError("Method must be implemented")

class GrAFConverter:

    def __init__(self, parser):
        self.parser = parser
        self.graph = graf.Graph()
        self.current_index = 0
        self.tiers_hierarchy = {}

    def next_index(self):
        index = self.current_index
        self.current_index += 1
        return index

    def convert(self):

        self._tiers_parent_list = []

        for tier in self.parser.get_root_tiers():
            self._convert_tier(tier, None, None)

        i = 0
        for t in self._tiers_parent_list:
            if t[1] is None:
                i += 1
                self.tiers_hierarchy[str(i)] = [t[0]]
            else:
                self._append_tier_to_hierarchy(self.tiers_hierarchy[str(i)], t[1], t[0])

    def _convert_tier(self, tier, parent_node, parent_annotation, parent_prefix = None):

        child_tiers = self.parser.get_child_tiers_for_tier(tier)

        if tier.linguistic_type is None:
            prefix = tier.name
            annotation_name = prefix
        else:
            try:
                annotation_name = tier.linguistic_type.encode("utf-8").replace(' ','_')
            except TypeError as typeError:
                annotation_name = tier.linguistic_type.replace(' ','_')

            prefix = annotation_name+"/"+tier.name

        has_regions = False

        if self.parser.tier_has_regions(tier):
            has_regions = True

        self._add_tier_in_hierarchy_list(prefix, parent_prefix)

        for annotation in self.parser.get_annotations_for_tier(tier, parent_annotation):
            regions = None

            if has_regions:
                regions = self.parser.region_for_annotation(annotation)

            node_id = NodeId(prefix, annotation.id)
            self._add_node(node_id, annotation, annotation_name, regions, parent_node)

            if child_tiers:
                for t in child_tiers:
                    self._convert_tier(t, node_id, annotation, prefix)

    def _add_tier_in_hierarchy_list(self, prefix, parent_prefix):
        if not (prefix, parent_prefix) in self._tiers_parent_list:
            self._tiers_parent_list.append((prefix, parent_prefix))

    def _append_tier_to_hierarchy(self, tiers_list, parent_tier, tier):
        for t in tiers_list:
            if isinstance(t, list):
                self._append_tier_to_hierarchy(t, parent_tier, tier)
            else:
                if t == parent_tier:
                    tiers_list.append([tier])

    def _add_node(self, node_id, annotation, annotation_name, regions, from_node_id):
        self._add_node_to_graph(node_id, regions, from_node_id)
        self._add_graf_annotation(annotation_name, annotation.id, node_id,
            annotation.value, annotation.features)

    def _add_graf_annotation(self, annotation_name, annotation_id,
                             annotation_ref, annotation_value, annotation_features=None):

        annotation = graf.Annotation(annotation_name, annotation_features,
            annotation_id)

        if annotation_value is not None:
            annotation.features['annotation_value'] = annotation_value

        self.graph.nodes[str(annotation_ref)].annotations.add(annotation)

        if annotation_name in self.graph.annotation_spaces:
            if annotation not in self.graph.annotation_spaces[annotation_name]:
                self.graph.annotation_spaces[annotation_name].add(annotation)
        else:
            annotation_space = graf.AnnotationSpace(annotation_name)
            annotation_space.add(annotation)

            self.graph.annotation_spaces.add(annotation_space)

    def _add_node_to_graph(self, node_id, regions=None,
                      from_node_id=None):

        node = graf.Node(str(node_id))

        if from_node_id is not None:
            edge_id = node_id.str_edge()
            edge = graf.Edge(edge_id, self.graph.nodes[str(from_node_id)], node)

            self.graph.edges.add(edge)

        if regions is not None:
            region_id = node_id.str_region()
            region = graf.Region(region_id, *regions)
            node.add_region(region)

            self.graph.regions.add(region)

        self.graph.nodes.add(node)

class Writer():
    """
    This class contain the methods to write the GrAF files.

    """

    def create_graf_xml_node(self, element_tree, annotations,
                             annotation_ref, node, region=None,
                             from_node=None, edge=None):
        """Create the nodes with the regions from
        a values with ids.

        Parameters
        ----------
        element_tree : Element Tree
            Xml element.
        annotation : object
            Annotation GrAF object.
        annotation_ref : str
            Reference that this annotation appoints to.
        node : object
            GrAF node object.
        region : object
            GrAF region node object.
        from_node : object
            GrAF node object representing the begin of an edge.
        edge : object
            GrAF edge node object.

        Returns
        -------
        element_tree : Element Tree
            Xml element.

        """

        graph_node = SubElement(element_tree, 'node',
                {'xml:id':node.id})

        if from_node is not None:
            SubElement(element_tree, 'edge', {'from':from_node.id,
                                              'to':node.id,
                                              'xml:id':edge.id})

        if region is not None:
            SubElement(graph_node, 'link', {'targets':region.id})

            SubElement(element_tree, 'region',
                    {'anchors':str(region.anchors[0])+" "+str(region.anchors[1]),
                     'xml:id':region.id})

        for annotation in annotations:
            element_tree = self.create_graf_xml_node_annotation(element_tree,
                annotation, annotation_ref)

        return element_tree

    def create_graf_xml_node_annotation(self, element_tree, annotation, annotation_ref):
        """Create the annotations of the nodes with
        ids.

        Parameters
        ----------
        element_tree : Element Tree
            Xml element.
        annotation : object
            Annotation graf object.
        annotation_ref : str
            Reference that this annotation appoints to.

        Returns
        -------
        element_tree : Element Tree
            Xml element.

        """

        graph_annotation = SubElement(element_tree, 'a',
                {'as':annotation.label,
                 'label':annotation.label,
                 'ref':annotation_ref,
                 'xml:id':annotation.id})

        features = SubElement(graph_annotation, 'fs')

        for feature in annotation.features._elements.items():
            key = feature[0]
            value = feature[1]
            SubElement(features, 'f', {'name':key}).text = value

        return element_tree

    def create_xml_graph_header(self, annotation, depends):
        """Create the GrAF header of the Xml document.

        Parameters
        ----------
        annotation : str
            Name of the annotation.
        depends : str
            Name of the node that the element belongs to.

        Returns
        -------
        element_tree : Element Tree
            Xml element.

        """

        element_tree = Element('graph',
                {'xmlns':'http://www.xces.org/ns/GrAF/1.0/'})
        graph_header = SubElement(element_tree,
            'graphHeader')
        SubElement(graph_header, 'labelsDecl')
        dependencies = SubElement(graph_header,
            'dependencies')

        if depends is not None and depends is not '':
            SubElement(dependencies, 'dependsOn', {'f.id':depends})

        annotation_spaces = SubElement(graph_header,
            'annotationSpaces')
        SubElement(annotation_spaces,
            'annotationSpace',{'as.id':annotation})

        return element_tree

    def generate_graf_files(self, graf, outputfile):

        for node in sorted(graf.nodes):
            if len(node.in_edges._by_ind) is not 0:
                edge = node.in_edges._by_ind[0]
                from_node = edge.from_node
            else:
                edge = None
                from_node = None

            if len(node.links) is not 0:
                links = node.links[0]
                region = links[0]
            else:
                region = None

            annotation_ref = node.id
            annotations = node.annotations

            annotation_name = str(node.id).split('/')[0]

            if annotation_name not in graf.additional_information:
                try:
                    dependencie = str(node.parent.id).split('/')[0]
                except AttributeError:
                    dependencie = None

                element_tree = self.create_xml_graph_header(annotation_name, dependencie)
            else:
                element_tree = graf.additional_information[annotation_name]

            graf.additional_information[annotation_name] = self.create_graf_xml_node(element_tree, annotations,
                annotation_ref, node, region, from_node, edge)

        filename = os.path.abspath(outputfile)
        (basedirname, file_extension) = os.path.splitext(outputfile)
        header = poioapi.io.header.HeaderFile(basedirname)
        header.filename = os.path.basename(os.path.splitext(filename)[0])
        header.primaryfile = os.path.basename(outputfile)
        header.dataType = 'text'

        for elements in graf.additional_information.items():
            file_name = elements[0]
            extension = file_name+".xml"
            filepath = basedirname+"-"+extension
            loc = os.path.basename(filepath)
            header.add_annotation(loc, file_name)
            file = open(filepath,'wb')
            element_tree = elements[1]
            doc = minidom.parseString(tostring(element_tree))
            file.write(doc.toprettyxml(indent='  ', encoding='utf-8'))
            file.close()

        header.create_header()