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
from xml.sax._exceptions import SAXParseException
from xml.dom.minidom import Document
from xml.dom import minidom
from poioapi import annotationtree
from poioapi import data
from xmltoanntree import ProcessContent

import txtrawfile
import pickle
import codecs
import header
import os
import xmltograf

class Parser():

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

    def parsing(self, data_hierarchy, annotation_tree):

        self.data_structure_type = data_hierarchy

        txt =  txtrawfile.CreateRawFile(self.filepath)
        txt.create_raw_file()

        self.header.author = 'CIDLeS'
        self.header.filename = txt.filename
        self.header.primaryfile = txt.file

        self.seek_tags(self.data_structure_type.data_hierarchy, 0)

        # Verify the elements
        for element in annotation_tree.elements():
            self.seek_elements(element, self.data_structure_type.data_hierarchy, 0)

        self.header.create_header()

    def seek_tags(self, hierarchy, level):
        level+=1
        for index in range(len(hierarchy)):
            if isinstance(hierarchy[index],list):
                self.seek_tags(hierarchy[index], level)
            else:
                level_list = (level, hierarchy[index], 0)
                self.level_map.append(level_list)

    def seek_elements(self, elements, labels, level):
        index = 0
        level+=1
        for element in elements:
            if isinstance(element, list):
                if isinstance(labels[index], list):
                    self.seek_elements(element, labels[index], level)
                else:
                    self.seek_elements(element, labels, level)
            else:
                if isinstance(labels[index], list):
                    label = labels[index + 1]
                else:
                    label = labels[index]

                index_map = 0
                need_increment = False

                # Get first element of hierarchy
                if level == 1 and index >= 1:
                    hierarchy_element = self.level_map[0]
                    depends_on = hierarchy_element[1]
                    increment = hierarchy_element[2] - 1

                    if element == elements[-1]:
                        label = labels[-1]

                elif level == 1:
                    depends_on = ''
                    hierarchy_element = self.level_map[0]
                    increment = hierarchy_element[2] - 1
                    need_increment = True
                else:
                    for item in self.level_map:
                        if label==item[1]:
                            hierarchy_level = item[0]
                            if index >= 1:
                                for item in self.level_map:
                                    if hierarchy_level==item[0]:
                                        depends_on = item[1]
                                        increment = item[2] - 1
                                        break
                            else:
                                hierarchy_element = self.level_map[index_map-1]
                                depends_on = hierarchy_element[1]
                                increment = hierarchy_element[2] - 1
                                need_increment = True
                        index_map+=1

                self.add_element(label,
                    element.get('annotation'), depends_on, increment)

                # Increment the dependency
                if need_increment:
                    for idx, item in enumerate(self.level_map):
                        if item[1] == label:
                            new_value = item[2] + 1
                            self.level_map[idx] = (item[0], item[1], new_value)
                            need_increment = False
                            break
                    need_increment = False

                index+=1

    def add_element(self, annotation, annotation_value, depends, increment):

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

        if level > 2 and annotation != 'word' \
        or (annotation == 'translation' or annotation == 'comment' or annotation == 'graid2'):
            doc = self.create_dependent_node(doc, graph,
                annotation, annotation_value, depends, increment)
        else:
            doc = self.create_node_region(doc, graph, depends, annotation,
                annotation_value, increment, filepath)

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
                              annotation_value, depends, depends_n):

        id_counter = len(doc.getElementsByTagName('a'))

        # Creating the features and the linkage
        a = doc.createElement("a")
        a.setAttribute("xml:id", annotation + "-"
        + str(id_counter)) # id
        a.setAttribute("label", annotation) # label
        a.setAttribute("ref", depends + "-n"
        + str(depends_n)) # ref
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

    def create_node_region(self, doc, graph, depends, annotation, annotation_value, increment, filepath):

        try:
            procContent = ProcessContent(filepath)
            procContent.process()
            ranges = procContent.get_tokenizer()

            index = len(ranges) - 1
            range = ranges[index]

            last_counter = int(range[1])
        except SAXParseException as sax_error:
            last_counter = 0

        counter = last_counter

        last_counter += len(annotation_value)

        seg_count = len(doc.getElementsByTagName('region'))

        # Creating the node with link
        node = doc.createElement("node")
        node.setAttribute("xml:id", annotation + "-n"
        + str(seg_count)) # Node number

        if depends != '':
            # Creating the link node
            link = doc.createElement("link")
            link.setAttribute("targets", depends + "-r"
            + str(increment)) # ref
            node.appendChild(link)

            # Creating the edge node
            edge = doc.createElement("edge")
            edge.setAttribute("from", depends + "-r"
            + str(increment)) # from node
            edge.setAttribute("to", annotation + "-r"
            + str(seg_count)) # to node
            graph.appendChild(edge)

        graph.appendChild(node)

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

class Render():

    def __init__(self, filepath):
        """Class's constructor.

        Parameters
        ----------
        filepath : str
            Path of the file to manipulate.

        """

        self.filepath = filepath
        basename = self.filepath.split('-header')
        self.basedirname = basename[0]
        self.basedir = os.path.dirname(self.filepath)
        self.level_map = []

    def writer(self):
        # read header file
        doc = minidom.parse(self.filepath)

        primary_data = doc.getElementsByTagName('primaryData')[0].getAttribute('loc')

        annotatios_files = doc.getElementsByTagName('annotation')

        for annotation in annotatios_files:
            loc = annotation.getAttribute('loc') # File name
            fid = annotation.getAttribute('f.id') # File id

        file = open(str(self.basedir)+ '/' + str(primary_data), 'r')
        res = file.readlines()
        file.close()

        i=0

        # Map the structure elements
        self.seek_tags(data.DataStructureTypeGraid().data_hierarchy, 0)
        values_list = []

        for strct_elem in self.level_map:
            file = self.basedirname+'-'+str(strct_elem[1])+'.xml'
            doc = minidom.parse(file)

            regions = doc.getElementsByTagName('region')

            procContent = ProcessContent(file)
            procContent.process()

            tokens = procContent.get_tokenizer()
            ids = procContent.get_token_id()

            if len(regions) is 0:
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

    def seek_tags(self, hierarchy, level):
        level+=1
        for index in range(len(hierarchy)):
            if isinstance(hierarchy[index],list):
                self.seek_tags(hierarchy[index], level)
            else:
                level_list = (level, hierarchy[index], 0)
                self.level_map.append(level_list)

#------------------------------------
#filepath = '/home/alopes/tests/pi.pickle'
#annotation_tree = annotationtree.AnnotationTree(data.DataStructureTypeGraid())

# Open the file
#file = open(filepath, "rb")
#annotation_tree.tree = pickle.load(file)

#Parser(filepath).parsing(data.DataStructureTypeGraid(), annotation_tree)
#------------------------------------
headerfile = '/home/alopes/tests/pi-header.hdr'
Render(headerfile).writer()
