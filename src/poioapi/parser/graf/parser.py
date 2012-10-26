# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
""" This document is to create the regions
of the words in the clause units one by one.
"""
import os

from xml.sax._exceptions import SAXParseException
from poioapi import annotationtree
from poioapi import data
import txtrawfile
from xmltoanntree import ProcessContent
from xml.dom.minidom import Document
from xml.dom import minidom

import pickle
import codecs
import header
import xmltograf

class GrafParser():

    def __init__(self, filepath):
        """Class's constructor.

        Parameters
        ----------
        filepath : str
            Path of the file to manipulate.

        """

        self.filepath = filepath
        basedirname = self.filepath.split('.')
        self.basedirname = basedirname[0]
        self.header = header.CreateHeaderFile(filepath)
        self.level_map = []

    def parsing(self, data_hierarchy):

        self.data_structure_type = data_hierarchy

        annotation_tree = annotationtree.AnnotationTree(self.data_structure_type.data_hierarchy)

        # Open the file
        file = open(self.filepath, "rb")
        annotation_tree.tree = pickle.load(file)

        txt =  txtrawfile.CreateRawFile(self.filepath)
        txt.create_raw_file()

        self.header.author = 'CIDLeS'
        self.header.filename = txt.filename
        self.header.primaryfile = txt.file

        self.seektags(self.data_structure_type.data_hierarchy, 0)

        # Verify the elements
        for element in annotation_tree.elements():
            self.seek_elements(element, self.data_structure_type.data_hierarchy, '')

        self.header.create_header()

        #self.add_element_xml('ann','ann_value','depends_b')
        graf = xmltograf.RendToGrAF(self.filepath)
        # Choose a type of GrAF Graid1/2, WfW or Gloss
        graf.parse_xml_graf('graid1')

    def seektags(self, hierarchy, level):
        level+=1
        for index in range(len(hierarchy)):
            if isinstance(hierarchy[index],list):
                self.seektags(hierarchy[index], level)
            else:
                level_list = (level, hierarchy[index])
                self.level_map.append(level_list)

    def seek_elements(self, element, label, depends_on):
        for index in range(len(element)):
            if index == 1:
                depends_on = label[index-1]
            if isinstance(element[index],list):
                try:
                    if isinstance(label[index], list):
                        self.seek_elements(element[index], label[index], depends_on)
                    else:
                        self.seek_elements(element[index], label, depends_on)
                except IndexError as indexError:
                    self.seek_elements(element[index], label, depends_on)
            else:
                self.add_element_xml(label[index],
                    element[index].get('annotation'), depends_on)

    def add_element_xml(self, annotation, annotation_value, depends):

        # See if the file exist
        # First see if the header is created and then do the rest
        # If the depends is '' nothing don't create the depends
        # Need a way to keep the track about the id

        first_element = self.level_map[0]
        if annotation==first_element[1]:
            return

        for item in self.level_map:
            if annotation==item[1]:
                level = item[0]
                break

        filepath = self.basedirname + '-' + annotation + '.xml'
        new_file = False

        try:
            with open(filepath) as f:
                doc = minidom.parse(filepath)
        except IOError as e:
            f = codecs.open(filepath,'w','utf-8')
            new_file = True

        if new_file:
            if level > 1 or (annotation == 'translation'
                             or annotation == 'comment'
                             or annotation == 'graid2'):
                doc = self.create_graf_header(annotation, depends)
            else:
                doc = self.create_graf_header(annotation, '')

            self.header.add_annotation(os.path.basename(filepath),annotation)

        graph = doc.getElementsByTagName('graph').item(0)

        if depends != '' and level > 2 and annotation != 'word' \
        or (annotation == 'translation' or annotation == 'comment'
            or annotation == 'graid2'):
            doc = self.create_dependent_node(doc, graph,
                annotation, annotation_value, depends)
        else:
            doc = self.create_node_region(doc, graph, annotation,
                annotation_value, filepath)

        if new_file:
            # Write the content in XML file
            f.write(doc.toprettyxml('  '))

            #Close XML file
            f.close()
        else:
            file = codecs.open(filepath,'w', 'utf-8')
            file.write(doc.toprettyxml('  '))
            file.close()

            file = codecs.open(filepath,'r', 'utf-8')
            lines = file.readlines()
            file.flush()
            file.close()

            file = codecs.open(filepath,'w', 'utf-8')
            for line in lines:
                if not line.isspace():
                    file.writelines(line)

            file.close()

    def create_dependent_node(self, doc, graph, annotation,
                              annotation_value, depends):

        id_counter = len(doc.getElementsByTagName('a'))

        # Creating the node with link
        node = doc.createElement("node")
        node.setAttribute("xml:id", annotation + "-n"
        + str(id_counter)) # Node number

        # Creating the node
        link = doc.createElement("link")
        link.setAttribute("targets", depends + "-r"
        + str(id_counter)) # ref
        node.appendChild(link)

        graph.appendChild(node)

        # Creating the features and the linkage
        a = doc.createElement("a")
        a.setAttribute("xml:id", annotation + "-"
        + str(id_counter)) # id
        a.setAttribute("label", annotation) # label
        a.setAttribute("ref", annotation + "-n"
        + str(id_counter)) # ref
        a.setAttribute("as", annotation) # as

        # Feature structure
        feature_st = doc.createElement("fs")
        feature = doc.createElement("f")
        feature.setAttribute("name",annotation)
        value = doc.createTextNode(annotation_value) # Value
        feature.appendChild(value)
        feature_st.appendChild(feature)

        a.appendChild(feature_st)
        graph.appendChild(a)

        return doc

    def create_node_region(self, doc, graph, annotation, annotation_value, filepath):
        try:
            procContent = ProcessContent(filepath)
            procContent.process()
            ranges = procContent.get_tokenizer()

            index = len(ranges) - 1
            range = ranges[index]

            last_counter = int(range[0])
        except SAXParseException as sax_error:
            last_counter = 0

        counter = last_counter

        last_counter += len(annotation_value)

        seg_count = len(doc.getElementsByTagName('region'))

        region = doc.createElement("region")
        region.setAttribute("xml:id", annotation + "-r"
        + str(seg_count)) # Region
        region.setAttribute("anchors",
            str(counter) + " " +
            str(last_counter)) # Anchors

        graph.appendChild(region)

        return doc

    def create_graf_header(self, annotation, depends):

        doc = Document()
        graph = doc.createElement("graph")
        graph.setAttribute("xmlns", "http://www.xces.org/ns/GrAF/1.0/")
        doc.appendChild(graph)

        # Header
        graphheader = doc.createElement("graphHeader")
        labelsdecl = doc.createElement("labelsDecl")
        graphheader.appendChild(labelsdecl)
        graph.appendChild(graphheader)

        if depends!='':
            dependencies = doc.createElement('dependencies')
            dependson = doc.createElement('dependsOn')
            dependson.setAttribute('f.id',depends)
            dependencies.appendChild(dependson)
            graphheader.appendChild(dependencies)

            ann_spaces = doc.createElement('annotationSpaces')
            ann_space = doc.createElement('annotationSpace')
            ann_space.setAttribute('as.id',annotation)
            ann_spaces.appendChild(ann_space)
            graphheader.appendChild(ann_spaces)

        return doc

    def coiso(self):
        # read header file
        doc = minidom.parse('/home/alopes/tests/pi_2-header.hdr')

        primary_data = doc.getElementsByTagName('primaryData')[0].getAttribute('loc')

        annotatios_files = doc.getElementsByTagName('annotation')

        for annotation in annotatios_files:
            loc = annotation.getAttribute('loc') # File name
            fid = annotation.getAttribute('f.id') # File id

        file = open('/home/alopes/tests/pi_2.txt', 'r')
        res = file.readlines()
        file.close()

        i=0

        # Map the structure elements
        self.seektags(data.DataStructureTypeGraid().data_hierarchy, 0)

        values_list = []

        for strct_elem in self.level_map:
            file = '/home/alopes/tests/pi_2-'+str(strct_elem[1])+'.xml'
            doc = minidom.parse(file)

            regions = doc.getElementsByTagName('region')

            procContent = ProcessContent(file)
            procContent.process()

            tokens = procContent.get_tokenizer()
            ids = procContent.get_token_id()

            if len(regions)==0:
                i = 0
                for node in doc.getElementsByTagName('f'):
                    nodes_value = (strct_elem[1],tokens[i],
                                   node.firstChild.nodeValue)
                    values_list.append(nodes_value)
                    i+=1
            else:
                for i in range(len(ids)):
                    nodes = (strct_elem[1], ids[i], tokens[i])
                    values_list.append(nodes)

        value_index=0

        self.annotation_tree = annotationtree.AnnotationTree(data.
        DataStructureTypeGraid.data_hierarchy)

        self.utterance_list = []

        for z in values_list:
            print(z)

        self.first_element = True
        first_range = True

        for line in res:
            self.line = line
            for element in data.DataStructureTypeGraid().data_hierarchy:
                if isinstance(element, list):
                    self.dive_element(element, value_index, values_list, list(), 0)
                else:
                    for el in values_list:
                        if el[0] == element and el[1]== str(value_index):
                            if isinstance(el[2], list):
                                if first_range:
                                    self.range = el[2]
                                    first_range = False
                                utterance = {  'id' : self.annotation_tree.next_annotation_id,
                                                'annotation' :  el[2]}
                            else:
                                utterance = {  'id' : self.annotation_tree.next_annotation_id,
                                    'annotation' :  el[2]}

                    self.utterance_list.append(utterance)

            if self.first_element:
                self.first_element = False

            self.annotation_tree.append_element(self.utterance_list)

            value_index+=1

        for element in self.annotation_tree.elements():
            print(element)
            print("\n")

    def dive_element(self, element, i, values_list, new_list, level):

        level+=1

        for index in range(len(element)):
            if isinstance(element[index],list):
              utterance = self.dive_element(element[index], i, values_list, list(), level)
            else:
                for el in values_list:
                    if el[0] == element[index] and el[1]== str(i):
                        if isinstance(el[2], list):
                            ranges = el[2]
                            if self.first_element:
                                begin = int(ranges[0])
                                end = int(ranges[1])
                            else:
                                begin = int(ranges[0]) - int(self.range[0])
                                end =  int(self.range[1]) - int(ranges[1]) \
                                       + (int(ranges[1]) - int(ranges[0])) + begin
                            value = self.line[begin:end]
                            utterance = {  'id' : self.annotation_tree.next_annotation_id,
                                            'annotation' :  value}
                        else:
                            utterance = {  'id' : self.annotation_tree.next_annotation_id,
                                            'annotation' :  el[2]}
            new_list.append(utterance)

        if level > 1:
            return new_list
        else:
            self.utterance_list.append([new_list])

#GrafParser('/home/alopes/tests/pi_2.pickle').parsing(data.DataStructureTypeGraid())
GrafParser('/home/alopes/tests/pi_2.pickle').coiso()
