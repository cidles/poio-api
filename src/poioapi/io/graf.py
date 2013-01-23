# -*- coding: utf-8 -*-
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

import codecs

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from xml.etree.ElementTree import Element, SubElement

class GrAFWriter():
    """
    This class contain the methods to write the GrAF files.

    """

    def create_node_with_region(self, element_tree, annotation,
                                annotation_id, annotation_ref,
                                annotation_value, node_id, region_id,
                                region, from_node_id, edge_id):
        """Create the nodes with the regions from
        a values with ids.

        Parameters
        ----------
        element_tree : Element Tree
            Xml element.
        annotation : str
            Name of the annotation.
        annotation_id : str
            Annotation identification.
        annotation_ref : str
            Reference that this annotation appoints to.
        annotation_value : str
            Value of the annotation.
        node_id : str
            Identification of the node.
        region_id : str
            Identification of the region.
        region : array_like
            Are the regions of the value word in the raw text.
        from_node_id : str
            Identification of the node of the region.
        edge_id : str
            Identification of the edge.

        Returns
        -------
        element_tree : Element Tree
            Xml element.

        """

        graph_node = SubElement(element_tree, 'node',
                {'xml:id':node_id})

        SubElement(graph_node, 'link', {'targets':region_id})

        if from_node_id is not None:
            SubElement(element_tree, 'edge', {'from':from_node_id,
                                              'to':node_id,
                                              'xml:id':edge_id})

        SubElement(element_tree, 'region',
                {'anchors':str(region[0])+" "+str(region[1]),
                 'xml:id':region_id})

        element_tree = self.create_node_annotation(element_tree,
            annotation, annotation_id, annotation_ref, annotation_value)

        return element_tree

    def create_node_annotation(self, element_tree, annotation,
                               annotation_id, annotation_ref,
                               annotation_value):
        """Create the annotations of the nodes with
        ids.

        Parameters
        ----------
        element_tree : Element Tree
            Xml element.
        annotation : str
            Name of the annotation.
        annotation_id : str
            Annotation identification.
        annotation_ref : str
            Reference that this annotation appoints to.
        annotation_value : str
            Value of the annotation.

        Returns
        -------
        element_tree : Element Tree
            Xml element.

        """

        graph_annotation = SubElement(element_tree, 'a',
                {'as':annotation,
                 'label':annotation,
                 'ref':annotation_ref,
                 'xml:id':annotation_id})

        features = SubElement(graph_annotation, 'fs')
        feature = SubElement(features, 'f', {'name':'annotation_value'})
        feature.text = annotation_value

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

class GrAFParser:
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