# -*- coding: utf-8 -*-
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT
""" This document contain the responsible
methods to write the GrAF files.
"""

from xml.etree.ElementTree import Element, SubElement

class GrAFWriter():
    """
    This class contain the methods to write the GrAF files.

    """

    def create_node_with_region(self, element_tree, dependency, annotation,
                                annotation_id, annotation_ref,
                                annotation_value, node_id, region_id,
                                region, from_node_id, edge_id):
        """Create the nodes with the regions from
        a values with ids.

        Parameters
        ----------
        element_tree : Element Tree
            Xml element.
        dependency : str
            Name of the node that the element belongs to.
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

        SubElement(element_tree, 'edge', {'from':from_node_id,
                                          'to':node_id,
                                          'xml:id':edge_id})

        SubElement(element_tree, 'region',
                {'anchors':str(region[0])+" "+str(region[1]),
                 'xml:id':region_id})

        if dependency is not None and dependency is not '':
            element_tree = self.create_node_annotation(element_tree,
                annotation, annotation_value, annotation_id, annotation_ref)

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