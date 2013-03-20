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
import codecs
import os
import re

from xml.dom import minidom

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from xml.etree.ElementTree import Element, SubElement, tostring

import graf
import poioapi.io.header

class Tier:
    __slots__ = [ 'name']

    def __init__(self, name):
        self.name = name

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

    #@abc.abstractmethod
    #def find_children_tiers_for_tier(self, tier):
    #    raise NotImplementedError("Method must be implemented")

    @abc.abstractmethod
    def get_annotations_for_tier(self, tier, annotation_parent=None):
        raise NotImplementedError("Method must be implemented")

    #@abc.abstractmethod
    #def add_elements_to_annotation_list(self, tier, annotations):
    #    raise NotImplementedError("Method must be implemented")

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

        #self.convert()

    def next_index(self):
        index = self.current_index
        self.current_index += 1
        return index

    def convert(self):

        for tier in self.parser.get_root_tiers():
            self._convert_tier(tier, None, None)

    #def _convert_tier(self, tier, parent_node, parent_annotation):
    def _convert_tier(self, tier, parent_node, parent_tier):

        child_tiers = self.parser.get_child_tiers_for_tier(tier)

        #for annotation in self.parser.get_annotations_for_tier(tier, parent_annotation):
        #for annotation in self.parser.get_annotations_for_tier(tier, parent_node):
        for annotation in self.parser.get_annotations_for_tier(tier, parent_tier):
            node_id = NodeId(tier.name, annotation.id)
            self._add_node(node_id, annotation, parent_node)
            if child_tiers:
                for t in child_tiers:
                    print(annotation)
                    #self._convert_tier(t, node_id, annotation)
                    self._convert_tier(t, node_id, parent_tier)

    def _add_node(self, node_id, annotation, from_node_id):
        self.add_node_to_graph(node_id, from_node_id=from_node_id)
        self.add_graf_annotation(annotation.value, annotation.id, node_id, annotation.features)

    #        annotations = self.parser.annotations_list
#
#        for tier in annotations:
#
#            regions = None
#            from_node = None
#
#            if tier['regions'] is not None:
#                regions = tier['regions']
#                if tier['parent_ref'] is not None:
#                    from_node = self.find_from_node_from_regions(tier['parent_ref'], tier['regions'])
#
#            if tier['annotation_ref'] is not None:
#                from_node = self.graph.nodes[tier['annotation_ref']]
#
#            annotation_ref = tier['prefix_name']+"/n"+tier['index_number']
#
#            self.add_graf_node(tier['index_number'], tier['prefix_name'], regions, from_node)
#            self.add_graf_annotation(tier['annotation_name'],
#                tier['annotation_id'], annotation_ref,
#                tier['features'])
#
#        return self.graph

    def add_graf_annotation(self, annotation_name, annotation_id,
                            annotation_ref, annotation_features=None):

        annotation = graf.Annotation(annotation_name, annotation_features,
            annotation_id)

        self.graph.nodes[str(annotation_ref)].annotations.add(annotation)

        annotation_space = graf.AnnotationSpace(annotation_name)
        annotation_space.add(annotation)

        self.graph.annotation_spaces.add(annotation_space)

    def add_node_to_graph(self, node_id, regions=None,
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

    def find_from_node_from_regions(self, parent_ref, anchors):

        for region in self.graph.regions:
            if parent_ref in region.id:
                if (int(region.anchors[0]) <= int(anchors[0]) <= int(region.anchors[1]))\
                and (int(region.anchors[0]) <= int(anchors[1]) <= int(region.anchors[1])):
                    node_id = re.sub(r"(.*)/r", r"\1/n", region.id)
                    node = self.graph.nodes[node_id]
                    return node

        return None

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

    def create_node_with_region_no_id(self, element_tree, depends, annotation,
                                      annotation_value, region, increment):
        """Create the nodes with the regions and
        generate the ids of the nodes, edges...
        and the rest of the GrAF elements.

        Parameters
        ----------
        element_tree : Element Tree
            Xml element.
        depends : str
            Name of the node that the element belongs to.
        annotation : str
            Name of the annotation.
        annotation_value : str
            Value of the annotation.
        region : array_like
            Are the regions of the value word in the raw text.
        increment : int
            It is the number node of the value.

        Returns
        -------
        element_tree : Element Tree
            Xml element.

        """

        seg_count = len(element_tree.getiterator('region'))

        graph_node = SubElement(element_tree, 'node',
                {'xml:id':annotation+"-n"+str(seg_count)})

        SubElement(graph_node, 'link', {'targets':annotation+"-r"+str(seg_count)})

        if depends != '':
            SubElement(element_tree, 'edge',
                    {'label':annotation,
                     'from':depends+"-n"+str(increment),
                     'to':annotation+"-n"+str(seg_count),
                     'xml:id':annotation+"-e"+str(seg_count)})

        SubElement(element_tree, 'region',
                {'anchors':str(region[0])+" "+str(region[1]),
                 'xml:id':annotation+"-r"+str(seg_count)})

        if depends is not None and depends is not '':
            element_tree = self.create_node_annotation_no_id(element_tree,
                annotation, annotation_value, annotation, seg_count)

        return element_tree

    def create_node_annotation_no_id(self, element_tree, annotation,
                                     annotation_value, depends, depends_number):
        """Create nodes that only have annotation
        and dependencies and generate the ids of
        the rest of the GrAF elements.

        Parameters
        ----------
        element_tree : Element Tree
            Xml element.
        annotation : str
            Name of the annotation.
        annotation_value : str
            Value of the annotation.
        depends : str
            Name of the node that the element belongs to.
        depends_number : int
            It is the number node of the value.

        Returns
        -------
        element_tree : Element Tree
            Xml element.

        """

        id_counter = len(element_tree.getiterator('a'))

        graph_annotation = SubElement(element_tree, 'a',
                {'as':annotation,
                 'label':annotation,
                 'ref':depends+"-n"+str(depends_number),
                 'xml:id':annotation+"-a"+str(id_counter)})

        features = SubElement(graph_annotation, 'fs')
        feature = SubElement(features, 'f', {'name':'annotation_value'})
        feature.text = annotation_value

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
        header.filename = os.path.splitext(filename)[0]
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

class XmlHandler(ContentHandler):

    def __init__(self):
        self.regions_list = []
        self.features_list = []
        self.link = ''
        self.edge_from = ''
        self.map = {}
        self.tag = ''
        self._root_element = 0
        self._buffer = ""
        self.hasregion = False
        self.elan_list = []
        self.tier_id = ''
        self.cv_id = ''
        self.time_slot_dict = dict()
        self.constraints_list = []
        self.linguistic_type_list = []

    def startElement(self, name, attrs):

        self.map[name] = ''
        self.tag = name

        if name == 'link':
            self.link = attrs.getValue('targets')

        if name == 'region':
            id = attrs.getValue('xml:id')
            att = attrs.getValue('anchors')
            tokenizer = att.split()
            values = (id, tokenizer,
                      self.edge_from)
            self.regions_list.append(values)
            self.hasregion = True

        if name == 'edge':
            self.edge_from = attrs.getValue('from')

        if name == 'a':
            ref = attrs.getValue('ref')
            id = attrs.getValue('xml:id')

            if self.hasregion:
                self.values = (id, self.edge_from)
            else:
                self.values = (id, ref)

    def characters (self, ch):
        self.map[self.tag] += ch

        # Check for root node
        if self._root_element == 1:
            self._buffer += ch

    def endElement(self, name):
        if name=='f':
            values = self.values
            id = values[0]
            ref = values[1]
            self.features_list.append((id, self.map[name], ref))

class Parser:
    """
    Class that handles the content of GrAF files.

    The class uses the ContentHandler from
    SAX XML.
    """

    def __init__(self, metafile):
        """Class's constructor.

        Parameters
        ----------
        metafile : str
            Path of the file to manipulate.

        """

        self.metafile = metafile

    def parse(self):
        """Return the important information about the
        different files (e.g. GrAF, elan,...). The gathered
        information contains tokens, regions and all the need
        data that will be used to help in the creation of the
        GrAF objects from the files or to create GrAF files
        from the same kind of files.

        """

        parser = make_parser()
        xml_handler = XmlHandler()
        parser.setContentHandler(xml_handler)

        # Handle the files encode
        try:
            f = codecs.open(self.metafile, 'r', 'utf-8')
            parser.parse(f)
        except UnicodeEncodeError as unicodeError:
            print(unicodeError)

            f = open(self.metafile, 'r')
            parser.parse(f)

        f.close()

        self.features_list = xml_handler.features_list
        self.regions_list = xml_handler.regions_list