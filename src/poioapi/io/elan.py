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

from __future__ import absolute_import
from collections import defaultdict

import os
import re
import codecs

from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.etree.ElementTree as ET

from poioapi.io import header
from poioapi.io.graf import GrAFWriter

from graf import Graph, GrafRenderer
from graf import Node, Edge
from graf import Annotation, AnnotationSpace
from graf import Region

class Elan:
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

        self.graf = GrAFWriter()

    def elan_to_graf(self):
        """This method will retrieve the parsed elements
        of an elan file. Then will create a GrAF object
        based in the information from the parsed elements.
        This method will also create the data structure
        hierarchy and theirs respective constraints.

        Returns
        -------
        graph : object
            GrAF object.

        """

        graph = Graph()

        no_structure = False

        tier_linguistic_map = dict()
        orphan_annotation_references_map = dict()

        # Find the dependencies in the hierarchy
        if len(self.data_structure_hierarchy) is not 0:
            self._find_hierarchy_parents(self.data_structure_hierarchy, None)
        else:
            no_structure = True

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

        self.anchors_dict = defaultdict(list)

        for tier in tiers:
            tier_id = tier.attrib['TIER_ID']
            linguistic_type_ref = tier.attrib['LINGUISTIC_TYPE_REF'].\
            replace(" ","_")

            if not tier_id in tier_linguistic_map.keys():
                tier_linguistic_map[tier_id] = linguistic_type_ref

        # First try with the tiers
        for tier_num, tier in enumerate(tiers):
            tier_id = tier.attrib['TIER_ID']
            linguistic_type_ref = tier.attrib['LINGUISTIC_TYPE_REF'].\
            replace(" ","_")

            try:
                parent_ref = tier.attrib['PARENT_REF']
            except KeyError as keyError:
                parent_ref = None
                from_node = None
                edge = None

            # Need to check if the tier element already exist
            if linguistic_type_ref not in self.xml_files_map.keys():
                # Creates the Xml Header (graphHeader)
                if no_structure is True:
                    if tier_num is 0:
                        dependecie = None
                    else:
                        if parent_ref is None:
                            dependecie = None
                        else:
                            dependecie = tier_linguistic_map[parent_ref]
                else:
                    dependecie = self.data_hierarchy_parent_dict[linguistic_type_ref]

                element_tree = self.graf.create_xml_graph_header(linguistic_type_ref,
                    dependecie)

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

                    anchors = (annotation_time_ref_1, annotation_time_ref_2)

                    index = re.sub("\D", "", annotation_id)

                    node_id = linguistic_type_ref+"/"+tier_id+"/n"+index
                    node = Node(node_id)

                    region_id = linguistic_type_ref+"/"+tier_id+"/r"+index
                    region = Region(region_id, *anchors)

                    if parent_ref is not None:
                        from_node = self._find_node(parent_ref, anchors)
                        if from_node is not None:
                            edge_id = "e"+index
                            edge = Edge(edge_id, from_node, node)
                            graph.edges.add(edge)
                    else:
                        self.anchors_dict[tier_id].append((node, anchors))

                    # Annotation
                    annotation_name = linguistic_type_ref
                    annotation = Annotation(annotation_name, None,
                        annotation_id)
                    annotation.features['annotation_value'] = annotation_value
                    annotation.features['time_slot1'] = \
                    child.attrib['TIME_SLOT_REF1']
                    annotation.features['time_slot2'] = \
                    child.attrib['TIME_SLOT_REF2']

                    node.annotations.add(annotation)
                    node.add_region(region)
                    
                    graph.regions.add(region)
                    graph.nodes.add(node)

                    annotation_ref = node_id

                    add_annotation = True
                    add_node = True

                elif child.tag == 'REF_ANNOTATION':
                    has_parent = False

                    annotation_id = child.attrib['ANNOTATION_ID']
                    annotation_value = child.find('ANNOTATION_VALUE').text
                    annotation_ref = child.attrib['ANNOTATION_REF']

                    look_tier = tier_linguistic_map[parent_ref]

                    if look_tier in self.xml_files_map.keys():
                        auxiliar_tree = self.xml_files_map[look_tier]

                        # Look for the parent node:
                        for el_tree in auxiliar_tree:
                            if el_tree.tag == 'node':
                                node_ref = el_tree.attrib['xml:id']
                            if el_tree.tag == 'a' and el_tree.attrib['xml:id'] == annotation_ref:
                                annotation_ref = node_ref
                                has_parent = True

                    if has_parent:
                        # Annotation
                        annotation_name = linguistic_type_ref
                        annotation = Annotation(annotation_name, None,
                            annotation_id)
                        annotation.features['annotation_value'] = annotation_value
                        annotation.features['ref_annotation'] = \
                        child.attrib['ANNOTATION_REF']
                        annotation.features['tier_id'] = tier_id

                        # Keep all the extra attributes of the annotations tags
                        for attribute in child.attrib:
                            if attribute != 'ANNOTATION_REF' and \
                               attribute != 'ANNOTATION_ID' and \
                               attribute != 'ANNOTATION_VALUE':
                                annotation.features[attribute] = child.attrib[attribute]

                        graph.nodes[annotation_ref].annotations.add(annotation)

                        add_annotation = True
                    else:
                        if look_tier in orphan_annotation_references_map.keys():
                            orphan_annotation_references_map[look_tier].\
                            append((linguistic_type_ref, annotation_id, annotation_value,
                                    child.attrib['ANNOTATION_REF'], tier_id, child.attrib))
                        else:
                            orphan_annotation_references_map[look_tier] = \
                            [(linguistic_type_ref, annotation_id, annotation_value,
                              child.attrib['ANNOTATION_REF'], tier_id, child.attrib)]

                # Add the annotation to the element tree
                if add_annotation:

                    annotation_space = AnnotationSpace(linguistic_type_ref)
                    annotation_space.add(annotation)

                    graph.annotation_spaces.add(annotation_space)

                    if add_node:
                        element_tree = self.graf.create_node_with_region(element_tree,
                            annotation, annotation_ref, node, region, anchors,
                            from_node, edge)
                    else:
                        element_tree = self.graf.create_node_annotation(element_tree,
                            annotation, annotation_ref)

            if no_structure:
                if not linguistic_type_ref in self.data_structure_hierarchy:
                    self.data_structure_hierarchy.append(linguistic_type_ref)

        # Find and place the orphan references because of the tiers order
        for orphan in orphan_annotation_references_map.items():
            reference = orphan[0]
            orphan_values = orphan[1]
            for values in orphan_values:
                annotation_name = values[0]
                annotation_id = values[1]
                annotation_value = values[2]
                annotation_ref = values[3]
                tier_id = values[4]

                auxiliar_tree = self.xml_files_map[reference]

                # Look for the parent node:
                for el_tree in auxiliar_tree:
                    if el_tree.tag == 'node':
                        node_ref = el_tree.attrib['xml:id']
                    if el_tree.tag == 'a' and el_tree.attrib['xml:id'] == annotation_ref:
                        annotation_node_ref = node_ref

                annotation = Annotation(annotation_name, None,
                    annotation_id)
                annotation.features['annotation_value'] = annotation_value
                annotation.features['ref_annotation'] = annotation_ref
                annotation.features['tier_id'] = tier_id

                # Keep all the extra attributes of the annotations tags
                for attribute in child.attrib:
                    if attribute != 'ANNOTATION_REF' and\
                       attribute != 'ANNOTATION_ID' and\
                       attribute != 'ANNOTATION_VALUE':
                        annotation.features[attribute] = child.attrib[attribute]

                graph.nodes[annotation_node_ref].annotations.add(annotation)

                annotation_space = AnnotationSpace(annotation_name)
                annotation_space.add(annotation)

                graph.annotation_spaces.add(annotation_space)

                element_tree = self.xml_files_map[annotation_name]

                self.xml_files_map[annotation_name] = \
                self.graf.create_node_annotation(element_tree,
                    annotation, annotation_node_ref)

        return graph

    def _find_node(self, parent_ref, anchors):
        """This method will try to find a parent
        node using to search the anchors. This
        anchors are the range/regions of a value.

        Parameters
        ----------
        parent_ref : str
            Identification of the parent of the node.
        anchors : array_like
            Values of the range to find the node.

        """

        for items in self.anchors_dict.items():
            if parent_ref == items[0]:
                for item in items[1]:
                    range = item[1]
                    if (int(range[0]) <= int(anchors[0]) <= int(range[1])) \
                    and (int(range[0]) <= int(anchors[1]) <= int(range[1])):
                        return item[0]
        return None

    def _find_hierarchy_parents(self, hierarchy, parent):
        """This method will search in the data structure
        hierarchy for the parents of each elements.

        Parameters
        ----------
        hierarchy : array_like
            Hierarchy of the data strcuture.
        parent : str
            Name of an element.

        """

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
        and all the important information. The header file
        it's created too.

        """

        self.header = header.HeaderFile(self.basedirname)
        self.header.filename = self.filename.split('.eaf')[0]
        self.header.primaryfile = self.filename
        self.header.dataType = 'Elan file' # Type of the origin data file

        for elements in self.xml_files_map.items():
            file_name = elements[0]
            extension = file_name+".xml"
            filepath = self.basedirname+"-"+extension
            loc = os.path.basename(filepath)
            self.header.add_annotation(loc, file_name)
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

        header_tag = SubElement(element_tree, 'header')

        data_structure = SubElement(header_tag, 'data_structure')
        
        SubElement(data_structure, 'hierarchy').text = \
        str(self.data_structure_hierarchy)

        tier_mapping = SubElement(header_tag,'tier_mapping')

        for values in self.data_structure_constraints.items():
            key = values[0]
            values = values[1]
            type = SubElement(tier_mapping,'type', {'name':key})
            for value in values:
                SubElement(type, 'tier').text = value

        file_tag = SubElement(element_tree, "file",
                {"data_type":self.header.dataType})

        miscellaneous = SubElement(file_tag, "miscellaneous")

        # Add the root element
        SubElement(miscellaneous, root.tag, root.attrib)

        for child in root:
            parent = SubElement(miscellaneous, child.tag, child.attrib)
            for lower_child in child:
                if lower_child.tag != "ALIGNABLE_ANNOTATION" and\
                   lower_child.tag != "REF_ANNOTATION" and\
                   lower_child.tag != "ANNOTATION_VALUE" and\
                   lower_child.tag != "ANNOTATION":
                    child_element = SubElement(parent, lower_child.tag,
                        lower_child.attrib)
                    if not str(lower_child.text).isspace() or\
                       lower_child.text is not None:
                        child_element.text = lower_child.text

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

class ElanWriter:
    """
    Class that will handle the writing of
    GrAF files into Elan files again.

    """

    def __init__(self, extinfofile, outputfile):
        """Class's constructor.

        Parameters
        ----------
        extinfofile : str
            Path of the metafile.
        outputfile : str
            Path and name of the new elan file.

        """

        self.extinfofile = extinfofile
        self.outputfile = outputfile

    def write_elan(self):
        """This method will look into the metafile
        and then reconstruct the Elan file.

        """

        tree = ET.parse(self.extinfofile)
        root = tree.getroot()

        miscellaneous = root.find('./file/miscellaneous')
        top_element = miscellaneous[0]

        element_tree = Element(top_element.tag, top_element.attrib)

        # Mapping the tiers LINGUISTIC_TYPE from the metafile
        tier_map_dict = dict()

        for tiers in root.findall('./header/tier_mapping/'):
            value = tiers.attrib['name'].replace(' ','_')
            for tiers_id in tiers:
                key = tiers_id.text
                tier_map_dict[key] = value

        # Need to know the if the lingyustic type is alignable
        linguisty_type = miscellaneous.findall('LINGUISTIC_TYPE')
        linguisty_type_dict = dict()

        for linguisty in linguisty_type:
            key = linguisty.attrib['LINGUISTIC_TYPE_ID'].replace(' ','_')
            value = linguisty.attrib['TIME_ALIGNABLE']
            linguisty_type_dict[key] = value

        for element in miscellaneous:

            if element.tag != 'miscellaneous' and\
               element.tag != 'ANNOTATION_DOCUMENT':

                parent_element = SubElement(element_tree, element.tag,
                    element.attrib)

                for child in element:
                    other_chid = SubElement(parent_element, child.tag,
                        child.attrib)
                    if not str(child.text).isspace() or\
                       child.text is not None:
                        other_chid.text = child.text

                if element.tag == 'TIER':
                    tier_id = element.attrib['TIER_ID']

                    try:
                        parent_ref = element.attrib['PARENT_REF']
                    except KeyError as keyError:
                        parent_ref = None

                    linguisty_id = element.attrib['LINGUISTIC_TYPE_REF']
                    linguisty_id = linguisty_id.replace(' ','_')

                    tree = ET.parse(self.extinfofile.replace("-extinfo","-"+linguisty_id))
                    graf_elements = tree.getroot()

                    xml_namespace = re.search('\{(.*)\}', graf_elements.tag).group()
                    attrib_namespace = "{http://www.w3.org/XML/1998/namespace}"

                    if linguisty_type_dict[linguisty_id] == "true":
                        for graf_element in graf_elements:
                            key = attrib_namespace+"id"
                            if (graf_element.tag == xml_namespace+"node")\
                            and (tier_id+"/" in graf_element.attrib[key]):
                                annotations = graf_elements.findall(xml_namespace+"a")
                                for annotation in annotations:
                                    ref = annotation.attrib['ref']

                                    if ref == graf_element.attrib[key]:
                                        annotation_id = annotation.attrib[attrib_namespace+"id"]
                                        feature_structure = annotation[0]
                                        annotation_value = feature_structure[0]
                                        time_slot_1 = feature_structure[2]
                                        time_slot_2 = feature_structure[1]

                                        features_map = {}
                                        features_map['ANNOTATION_ID'] = annotation_id
                                        features_map['TIME_SLOT_REF1'] = time_slot_1.text
                                        features_map['TIME_SLOT_REF2'] = time_slot_2.text

                                        for feature_element in feature_structure:
                                            if feature_element.attrib['name'] != 'annotation_value' and\
                                               feature_element.attrib['name'] != 'time_slot1' and\
                                               feature_element.attrib['name'] != 'time_slot2':
                                                key = feature_element.attrib['name']
                                                features_map[key] = feature_element.text

                                        if linguisty_type_dict[linguisty_id] == 'true':
                                            annotation_element = SubElement(parent_element,
                                                'ANNOTATION')
                                            alignable_annotation = SubElement(annotation_element,
                                                'ALIGNABLE_ANNOTATION',features_map)
                                            SubElement(alignable_annotation,
                                                'ANNOTATION_VALUE').text = annotation_value.text
                    else:
                        annotations = graf_elements.findall(xml_namespace+"a")

                        tree = ET.parse(self.extinfofile.replace("-extinfo",
                            "-"+tier_map_dict[parent_ref]))
                        parent_elements = tree.getroot()
                        parent_annotations = parent_elements.findall(xml_namespace+"a")

                        for annotation in annotations:
                            annotation_id = annotation.attrib[attrib_namespace+"id"]
                            feature_structure = annotation[0]

                            annotation_tier_id = feature_structure[0].text
                            ref_annotation_id = feature_structure[1].text
                            annotation_value = feature_structure[2].text

                            features_map = {}
                            features_map['ANNOTATION_ID'] = annotation_id
                            features_map['ANNOTATION_REF'] = ref_annotation_id

                            for feature_element in feature_structure:
                                if feature_element.attrib['name'] != 'ref_annotation' and\
                                   feature_element.attrib['name'] != 'annotation_value' and\
                                   feature_element.attrib['name'] != 'tier_id':
                                    key = feature_element.attrib['name']
                                    features_map[key] = feature_element.text

                            for parent_annotation in parent_annotations:
                                if parent_annotation.attrib['ref'] == annotation.attrib['ref']:
                                    if annotation_tier_id == tier_id:
                                        annotation = SubElement(parent_element, 'ANNOTATION')
                                        ref_annotation = SubElement(annotation,
                                            'REF_ANNOTATION',features_map)
                                        SubElement(ref_annotation, 'ANNOTATION_VALUE').text =\
                                        annotation_value

                                        break

        file = open(self.outputfile,'wb')
        doc = minidom.parseString(tostring(element_tree))
        file.write(doc.toprettyxml(indent='    ', encoding='UTF-8'))
        file.close()