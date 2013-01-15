# -*- coding: utf-8 -*-
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

import os
import re
import codecs

from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.etree.ElementTree as ET

from poioapi.io import header

from graf import Graph, GrafRenderer
from graf import Node, Edge
from graf import Annotation, AnnotationSpace
from graf import Region

class Elan:
    """
    Class that will handle elan files.

    """

    def __init__(self, filepath, data_structure_hierarchy):
        """Class's constructor.

        Parameters
        ----------
        filepath : str
            Path of the elan file.

        """

        self.filename = os.path.basename(filepath)
        self.filepath = filepath
        (self.basedirname, _) = os.path.splitext(os.path.abspath(self.filepath))

        self.data_structure_hierarchy = data_structure_hierarchy.data_hierarchy
        self.data_structure_constraints = data_structure_hierarchy.data_hierarchy_const

        self.data_hierarchy_parent_dict = dict()

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

        # Find the dependencies in the hierarchy
        self._find_hierarchy_parents(self.data_structure_hierarchy, None)

        tree = ET.parse(self.filepath)
        doc = tree.getroot()

        time_order = doc.find('TIME_ORDER')
        time_order_dict = dict()

        for time in time_order:
            key = time.attrib['TIME_SLOT_ID']
            try:
                value = time.attrib['TIME_VALUE']
            except KeyError as keyError:
                value = 0
            time_order_dict[key] = value

        tiers = doc.findall('TIER')
        tiers_number = 0

        # First try with the tiers
        for tier in tiers:
            node_id = "tier-n"+str(tiers_number)
            tier_node = Node(node_id)
            tier_id = tier.attrib['TIER_ID']
            linguistic_type_ref = tier.attrib['LINGUISTIC_TYPE_REF'].replace(" ","_")

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

                dependecie = self.data_hierarchy_parent_dict[linguistic_type_ref]
                if dependecie is not None:
                    SubElement(dependencies, 'dependsOn', {'f.id':dependecie})

                annotation_spaces = SubElement(graph_header,
                    'annotationSpaces')
                SubElement(annotation_spaces,'annotationSpace',
                        {'as.id':linguistic_type_ref})

                self.xml_files_map[linguistic_type_ref] = element_tree
            else:
                element_tree = self.xml_files_map[linguistic_type_ref]

            # Add to the constraint in the data structure hierarchy
            if linguistic_type_ref in self.data_structure_constraints:
                self.data_structure_constraints[linguistic_type_ref].append(tier_id)
            else:
                self.data_structure_constraints[linguistic_type_ref] = [tier_id]

            for child in tier.getiterator():
                add_annotation = False
                add_node = False

                if child.tag == 'ALIGNABLE_ANNOTATION':
                    annotation_time_ref_1 = str(time_order_dict[
                                            child.attrib['TIME_SLOT_REF1']])
                    annotation_time_ref_2 = str(time_order_dict[
                                            child.attrib['TIME_SLOT_REF2']])
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
                                           +" "+annotation_time_ref_2,
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

        return graph

    def _find_hierarchy_parents(self, hierarchy, parent):
        for index, element in enumerate(hierarchy):
            if isinstance(element, list):
                self._find_hierarchy_parents(element, parent)
            else:
                self.data_hierarchy_parent_dict[element] = parent
                if index is 0:
                    parent = element

    def generate_graf_files(self):
        """This method will create the GrAF Xml files.
        But first is need to create the GrAF object in
        order to get the values.
        This method will also create a metafile that will
        gathered all the data information to recreate the
        elan files and to access to the data structure
        hierarchy, the vocabulary, the media descriptor
        and all the important information.

        """

        self.header = header.HeaderFile(self.basedirname)
        self.header.filename = self.filename.split('.eaf')[0]
        self.header.primaryfile = self.filename
        self.header.dataType = 'Elan file' # Type of the origin data file

        for elements in self.xml_files_map.items():
            file_name = elements[0]
            extension = file_name+".xml"
            self.header.add_annotation(extension, file_name)
            filepath = self.basedirname+"-"+extension
            file = open(filepath,'wb')
            element_tree = elements[1]
            doc = minidom.parseString(tostring(element_tree))
            file.write(doc.toprettyxml(indent='  ', encoding='utf-8'))
            file.close()

        self.header.create_header()

        # Generating the metafile
        tree = ET.parse(self.filepath)
        root = tree.getroot()

        # Generate the metadata file
        element_tree = Element('metadata')

        SubElement(element_tree, 'header_file').text =\
        os.path.basename(self.header.filename)

        data_structure = SubElement(element_tree,
            'data_structure_hierarchy')
        structure = SubElement(data_structure,
            'hierarchy').text =\
        str(self.data_structure_hierarchy)

        constraints = SubElement(data_structure,'constraints')

        for values in self.data_structure_constraints.items():
            key = values[0]
            values = values[1]
            SubElement(constraints,'constraint', {key:values})

        file_tag = SubElement(element_tree, "file",
                {"data_type":self.header.dataType})

        miscellaneous = SubElement(file_tag, "miscellaneous")

        # Add the root element
        SubElement(miscellaneous, root.tag, root.attrib)

        for child in root:
            if child.tag != "ALIGNABLE_ANNOTATION" and\
               child.tag != "REF_ANNOTATION" and\
               child.tag != "ANNOTATION_VALUE" and\
               child.tag != "ANNOTATION":
                if child.tag == "TIER":
                    SubElement(miscellaneous, child.tag, child.attrib)
                else:
                    miscellaneous.append(child)

        filename = self.basedirname+"-extinfo.xml"
        file = open(filename,'wb')
        doc = minidom.parseString(tostring(element_tree))
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