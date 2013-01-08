# -*- coding: utf-8 -*-
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
"""This module contains classes to access Elan data.
The class Eaf is a low level API to .eaf files.

EafGlossTree, EafPosTree, etc. are the classes to
access the data via tree, which also contains the
original .eaf IDs. Because of this EafTrees are
read-/writeable.
"""

import os
import re
import codecs

from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.etree.ElementTree as ET

from poioapi.io import header
from poioapi.io.parser import ElanParser

from graf import Graph, GrafRenderer
from graf import Node, Edge
from graf import Annotation, AnnotationSpace
from graf import Region

class Elan:
    """
    Class that will handle elan files.

    """

    def __init__(self, filepath):
        """Class's constructor.

        Parameters
        ----------
        filepath : str
            Path of the elan file.

        """

        self.filename = os.path.basename(filepath)
        self.filepath = filepath
        (self.basedirname, _) = os.path.splitext(os.path.abspath(self.filepath))

        # Create the header file
        self.header = header.CreateHeaderFile(self.basedirname)
        self.data_structure_hierarchy = []

        self.xml_files_map = {}

    def elan_to_graf(self):
        """This method will recieve the parsed elements
        of an elan file. Then will create a GrAF object
        based in the information from the parsed elements.
        This method will also create the data structure
        hierarchy and theirs respective constraints.

        Returns
        -------
        graph : object
            GrAF object.

        See Also
        --------
        _create_data_structure

        """

        graph = Graph()

        tree = ET.parse(self.filepath)
        doc = tree.getroot()
        tiers = doc.findall('TIER')

        # Mandatory to give an author to the file
        self.header.author = 'CIDLeS'
        self.header.filename = self.filename.split('.eaf')[0]
        self.header.primaryfile = self.filename
        self.header.dataType = 'Elan file' # Type of the origin data file

        tiers_number = 0

        # First try with the tiers
        for tier in tiers:
            node_id = "tier-n"+str(tiers_number)
            tier_node = Node(node_id)
            tier_id = tier.attrib['TIER_ID']
            linguistic_type_ref = tier.attrib['LINGUISTIC_TYPE_REF']

            self.header.add_annotation(self.filename, linguistic_type_ref)

            # Need to check if the tier element already exist
            if linguistic_type_ref not in self.xml_files_map.keys():
                # Creates the Xml Header (graphHeader)
                element_tree = Element('graph',
                        {'xmlns':'http://www.xces.org/ns/GrAF/1.0/'})
                graph_header = SubElement(element_tree,
                    'graphHeader')
                SubElement(graph_header, 'labelsDecl')
                dependencies = SubElement(graph_header,
                    'dependencies')
                SubElement(dependencies, 'dependsOn', {'f.id':'None'})
                annotation_spaces = SubElement(graph_header,
                    'annotationSpaces')
                SubElement(annotation_spaces,'annotationSpace',
                        {'as.id':linguistic_type_ref})

                self.xml_files_map[linguistic_type_ref] = element_tree
            else:
                element_tree = self.xml_files_map[linguistic_type_ref]

            for child in tier.getiterator():
                add_annotation = False
                add_node = False

                if child.tag == 'ALIGNABLE_ANNOTATION':
                    annotation_time_ref_1 = child.attrib['TIME_SLOT_REF1']
                    annotation_time_ref_2 = child.attrib['TIME_SLOT_REF2']
                    annotation_id = child.attrib['ANNOTATION_ID']
                    annotation_value = child.find('ANNOTATION_VALUE').text

                    anchors = [annotation_time_ref_1, annotation_time_ref_2]

                    index = re.sub("\D", "", annotation_id)

                    node_id = tier_id+"-n"+index
                    node = Node(node_id)

                    region_id = tier_id+"-r"+index
                    region = Region(region_id, *anchors)

                    edge_id = child.tag+"-e"+index
                    edge = Edge(edge_id, tier_node, node)

                    # Annotation
                    annotation_name = linguistic_type_ref
                    annotation = Annotation(annotation_name, None,
                        annotation_id)
                    annotation.features['annotation_value'] = annotation_value

                    node.annotations.add(annotation)
                    node.add_region(region)

                    graph.regions.add(region)
                    graph.edges.add(edge)
                    graph.nodes.add(node)

                    annotation_ref = node_id

                    add_annotation = True
                    add_node = True

                elif child.tag == 'REF_ANNOTATION':
                    annotation_id = child.attrib['ANNOTATION_ID']
                    annotation_value = child.find('ANNOTATION_VALUE').text
                    annotation_ref = child.attrib['ANNOTATION_REF']

                    add_annotation = True

                # Add the annotation to the element tree
                if add_annotation:
                    if add_node:
                        graph_node = SubElement(element_tree, 'node',
                                {'xml:id':node_id})
                        # Link
                        SubElement(graph_node, 'link', {'targets':region_id})
                        # Edge
                        SubElement(element_tree, 'edge', {'from':tier_node.id,
                                                          'to':node_id,
                                                          'xml:id':edge_id})
                        # Region
                        SubElement(element_tree, 'region',
                                {'anchors':annotation_time_ref_1
                                           +" "+annotation_time_ref_1,
                                 'xml:id':region_id})

                    annotation_space = AnnotationSpace(linguistic_type_ref)
                    annotation_space.add(annotation)

                    graph.annotation_spaces.add(annotation_space)

                    graph_annotation = SubElement(element_tree, 'a',
                            {'as':linguistic_type_ref,
                             'label':linguistic_type_ref,
                             'ref':annotation_ref,
                             'xml:id':annotation_id})
                    features = SubElement(graph_annotation, 'fs')
                    feature = SubElement(features, 'f',
                            {'name':'annotation_value'})
                    feature.text = annotation_value

            tiers_number+=1

        for tir in self.xml_files_map.items():
            filepath = self.basedirname+"-"+tir[0]+".xml"
            file = open(filepath,'wb')
            doc = minidom.parseString(tostring(tir[1]))
            file.write(doc.toprettyxml(indent='  ', encoding='utf-8'))
            file.close()

        # Close the header file
        self.header.create_header()

        return graph

    def _create_graf_files(self, graph, header, data_structure):
        """This method will create the GrAF Xml files.
        But first is need to create the GrAF object in
        order to get the values.
        This method will also create a metafile that will
        gathered all the data information to recreate the
        elan files and to access to the data structure
        hierarchy, the vocabulary, the media descriptor
        and all the important information.

        Parameters
        ----------
        graph : object
            GrAF object.
        header : object
            Header object.
        data_structure : array_like
            Array like with the data structure hierarchy.

        """

        for tree_element in self.xml_files_map.items():
            tier_name = tree_element[0]
            filepath = self.basedirname+"-"+tier_name+".xml"
            file = open(filepath,'wb')
            element_tree = tree_element[1]
            doc = minidom.parseString(tostring(element_tree))
            file.write(doc.toprettyxml(indent='  ', encoding='utf-8'))
            file.close()

        # Generate the metadata file
        metafile_tree = Element('metadata')

        SubElement(metafile_tree, 'header_file').text =\
        os.path.basename(header.filename)

        SubElement(metafile_tree, 'data_structure_hierarchy').text =\
        str(data_structure)

        file_tag = SubElement(metafile_tree, "file",
                {"data_type":header.dataType})

        if graph.additional_information is not None:
            miscellaneous = SubElement(file_tag, "miscellaneous")
            current_parent_element = None
            for element in graph.additional_information:
                tag = element[0]
                attributes = element[1]

                try:
                    depends = [depends for depends in element
                               if 'DEPENDS - ' in
                                  depends]
                except IndexError as indexError:
                    depends = None

                try:
                    tag_value = [tag_value for tag_value in element
                                 if 'VALUE - ' in
                                    tag_value]
                except IndexError as indexError:
                    tag_value = None

                attribute_map = {}

                for attribute in attributes:
                    attr = attribute.split(' - ')
                    name = attr[0]
                    val = attr[1]
                    attribute_map[name] = val

                if not depends:
                    current_parent_element = SubElement(miscellaneous,
                        tag, attribute_map)
                    if tag_value:
                        value = tag_value[0].split(' - ')[1]
                        current_parent_element.text = value
                else:
                    if tag_value:
                        value = tag_value[0].split(' - ')[1]
                        SubElement(current_parent_element, tag,
                            attribute_map).text = value
                    else:
                        SubElement(current_parent_element, tag,
                            attribute_map)

        filename = self.basedirname+"-metafile.xml"
        file = open(filename,'wb')
        doc = minidom.parseString(tostring(metafile_tree))
        file.write(doc.toprettyxml(indent='  ', encoding='utf-8'))
        file.close()

    def graph_rendering(self, outputfile, graph):
        """This method will convert a GrAF object to a
        Xml files respecting GrAF standards.
        To use the rendering is need to install the
        Graf-Python Library,

        Parameters
        ----------
        outputfile : str
            Path to the outputfile with the renderer GrAF.
        graph : object
            GrAF object.

        """

        graf_render = GrafRenderer(outputfile+"_tmp")
        graf_render.render(graph)

        # Indent the Xml file
        file = codecs.open(outputfile,'w','utf-8')
        xml = minidom.parse(outputfile+"_tmp")
        file.write(xml.toprettyxml(' '))
        file.close()

        # Delete the temp file
        os.remove(outputfile+"_tmp")