# -*- coding: utf-8 -*-
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
""" This document contain the responsible
methods to generate and parse the GrAF files.
"""

import os
import pickle
import codecs

from xml.dom.minidom import Document
from xml.dom import minidom

from poioapi import annotationtree
from poioapi import data
from poioapi.io import header
from poioapi.io.analyzer import XmlContentHandler

class Writer():

    def __init__(self, annotation_tree, header_file):
        """Class's constructor.

        Parameters
        ----------
        filepath : str
            Path of the file to manipulate.

        """

        self.filepath = header_file
        (self.basedirname, _) = os.path.splitext(os.path.abspath(self.filepath))

        # Create the header file
        self.header = header.CreateHeaderFile(self.basedirname)

        self.level_map = []
        self.annotation_tree = annotation_tree
        self.xml_files_list = []
        self.xml_files_content = {}

    def write(self):

        self.data_structure_type = self.annotation_tree.data_structure_type

        # Creates the raw file
        self.create_raw_file()

        # Mandatory to give an author to the file
        self.header.author = 'CIDLeS'
        self.header.filename = os.path.basename(self.basedirname)
        self.header.primaryfile = os.path.basename(self.basedirname)+".txt"

        # Map the elements in the data structure type
        self.seek_tags(self.data_structure_type.data_hierarchy, 0)

        # Map that will contain the xml contexts
        self.xml_files_content = dict((hierarchy[1],None)
            for hierarchy in self.level_map)

        self.last_region_value = 0
        previous_region_value = 0

        # Verify the elements
        for index, element in enumerate(self.annotation_tree.elements()):
            if index > 0:
                self.last_region_value += previous_region_value
                previous_region_value = len(element[0].get('annotation'))
            else:
                previous_region_value = len(element[0].get('annotation'))

            self.seek_elements(element,
                self.data_structure_type.data_hierarchy, 0)

        # Close the header file
        self.header.create_header()

        # Creates the result XML docs for each element in the data
        # structure hierarchy
        for path in self.xml_files_list:
            file_to_find = os.path.basename(path)
            new_file = file_to_find.split('.')
            new_file = new_file[0].split('-')
            with codecs.open(path, 'w', 'utf-8') as f:
                for value in self.xml_files_content.items():
                    if value[0]==new_file[1]:
                        f.write(value[1].toprettyxml('  '))
                f.close()

    def seek_tags(self, hierarchy, level):
        level+=1
        for index in range(len(hierarchy)):
            if isinstance(hierarchy[index],list):
                self.seek_tags(hierarchy[index], level)
            else:
                level_list = (level,
                              hierarchy[index].replace(' ','_'), 0)
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

                label = label.replace(' ', '_')

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
                                hierarchy_element = \
                                self.level_map[index_map-1]
                                depends_on = hierarchy_element[1]
                                increment = hierarchy_element[2] - 1
                                need_increment = True
                        index_map+=1

                if element.get('region') is None:
                    self.add_element(label,
                        element.get('annotation'), None, depends_on, increment)
                else:
                    self.add_element(label,
                        element.get('annotation'), element.get('region'), depends_on, increment)

                # Increment the dependency
                if need_increment:
                    for idx, item in enumerate(self.level_map):
                        if item[1] == label:
                            new_value = item[2] + 1
                            self.level_map[idx] = (item[0], item[1],
                                                   new_value)
                            need_increment = False
                            break
                    need_increment = False

                index+=1

    def add_element(self, annotation, annotation_value, region, depends,
                    increment):

        # See if the file exist
        # First see if the header is created and then do the rest
        # If the depends is '' nothing don't create the depends
        # Need a way to keep the track about the id

        for item in self.level_map:
            if annotation==item[1]:
                level = item[0]
                break

        filepath = self.basedirname + '-' + annotation + '.xml'
        new_file = False

        if self.xml_files_content[annotation] == None:
            new_file = True
            self.xml_files_list.append(filepath)
        else:
            doc = self.xml_files_content[annotation]

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
        or (annotation == 'translation' or annotation == 'comment'
            or annotation == 'graid2'):
            doc = self.create_dependent_node(doc, graph,
                annotation, annotation_value, depends, increment)
        else:
            doc = self.create_node_region(doc, graph, depends, annotation,
                annotation_value, region, increment)

        self.xml_files_content[annotation] = doc

    def create_dependent_node(self, doc, graph, annotation,
                              annotation_value, depends, depends_n):

        id_counter = len(doc.getElementsByTagName('a'))

        # Creating the features and the linkage
        a = doc.createElement("a")
        a.setAttribute("xml:id", annotation + "-a"
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

    def create_node_region(self, doc, graph, depends, annotation, annotation_value, region, increment):

        seg_count = len(doc.getElementsByTagName('region'))

        # Creating the node with link
        node = doc.createElement("node")
        node.setAttribute("xml:id", annotation + "-n"
        + str(seg_count)) # Node number

        if depends=='':
            increment+=1

        # Creating the link node
        link = doc.createElement("link")
        link.setAttribute("targets", annotation + "-r"
        + str(increment)) # ref
        node.appendChild(link)

        graph.appendChild(node)

        if depends != '':
            # Creating the edge node
            edge = doc.createElement("edge")
            edge.setAttribute("xml:id", annotation + "-e"
            + str(seg_count)) # edge id
            edge.setAttribute("from", depends + "-n"
            + str(increment)) # from node
            edge.setAttribute("to", annotation + "-n"
            + str(seg_count)) # to node

            graph.appendChild(edge)

        if depends != '':
            begin = int(region[0]) + self.last_region_value
            end = int(region[1]) + self.last_region_value
        else:
            if self.last_region_value is 0:
                begin = self.last_region_value
            else:
                begin = self.last_region_value + 1
            end = begin + len(annotation_value) - 1

        region = doc.createElement("region")
        region.setAttribute("xml:id", annotation + "-r"
        + str(seg_count)) # Region
        region.setAttribute("anchors",
            str(begin) + " " +
            str(end)) # Anchors

        graph.appendChild(region)

        if depends != '':
            id_counter = len(doc.getElementsByTagName('a'))

            # Creating the features and the linkage
            a = doc.createElement("a")
            a.setAttribute("xml:id", annotation + "-a"
            + str(id_counter)) # id
            a.setAttribute("label", annotation) # label
            a.setAttribute("ref", annotation + "-n"
            + str(seg_count)) # ref
            a.setAttribute("as", annotation) # as

            # Feature structure
            feature_st = doc.createElement("fs")
            feature = doc.createElement("f")
            feature.setAttribute("name",'string')
            value = doc.createTextNode(annotation_value) # Value
            feature.appendChild(value)
            feature_st.appendChild(feature)

            a.appendChild(feature_st)

            graph.appendChild(a)

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

        if depends != '':
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

    def create_raw_file(self):
        """Creates an txt file with the data in the
        Annotation Tree file. Passing only the sentences.

        See Also
        --------
        create_raw_xml : Function the converts the data
        to an xml only with the regions.

        """

        file = os.path.abspath(self.basedirname + '.txt')
        f = codecs.open(file,'w', 'utf-8') # Need the encode

        # Verify the elements
        for element in self.annotation_tree.elements():

            # Get the utterance
            utterance = element[0]

            # Write the content to the txt file
            f.write(utterance.get('annotation') + '\n')

        # Close txt file
        f.close()

class Parser():

    def __init__(self, header_file):
        """Class's constructor.

        Parameters
        ----------
        filepath : str
            Path of the file to manipulate.

        """

        self.filepath = header_file
        (self.basedirname, _) = os.path.splitext(os.path.abspath(self.filepath))
        self.dirname = os.path.dirname(self.filepath)

    def load_as_graf(self):

        """
        gparser = GraphParser()

        file_stream = codecs.open(file, "r", "utf-8")

        graph = gparser.parse(file_stream)

        return graph

        """

        pass

    def load_as_tree(self, data_hierarchy):

        # Initialize the variable
        self.annotation_tree = annotationtree.AnnotationTree(data_hierarchy)

        # Read header file
        doc_header = minidom.parse(self.filepath)

        # Get the primary file. The file contain the raw text
        primary_file = doc_header.getElementsByTagName('primaryData')[0].\
        getAttribute('loc')

        # Get all the lines from the primary file
        txtfile = codecs.open(self.dirname+"/"+primary_file,'r', 'utf-8')
        self.txtlines = txtfile.readlines()
        txtfile.close()

        files_list = []
        annotatios_files = doc_header.getElementsByTagName('annotation')

        # Get the files to look for
        for annotation in annotatios_files:
            loc = annotation.getAttribute('loc') # File name
            fid = annotation.getAttribute('f.id') # File id
            files_list.append((fid, loc))

        tokens_list = []
        features_list = []

        for file in files_list:
            content = XmlContentHandler(self.dirname+'/'+file[1])
            content.process()

            features_map = content.get_features_map()
            tokens_map = content.get_tokens_map()

            features_list.append(features_map)
            tokens_list.append(tokens_map)

        self.elements_list = []

        for features in features_list:
            for feature in features:
                self.elements_list.append(feature)

        self.tree = []
        counter = 0

        for tokens in tokens_list:
            for token in tokens:
                if token[2]=='':
                    self._dependency = token[0].replace('-r','-n')
                    self.clear_list = []
                    self.elements_sort(data_hierarchy, self._dependency)
                    self.utterance = self.retrieve_string(token[1],counter)
                    self.annotation_tree.append_element(self.append_element(
                        data_hierarchy, [], token[2], 0, 0))
                    # A tree to a pickle
                    #self.tree.append(self.append_element(data_hierarchy, [], token[2], 0, 0))
                    counter+=1

        return self.annotation_tree

    def retrieve_string(self, token, counter):
        begin = int(token[0]) * 0
        end = int(token[1]) - int(token[0])
        string = self.txtlines[counter]
        return  string[begin:end]

    def append_element(self, elements, new_list, depends, depends_n, level):
        level+=1
        empty_list = []
        while depends_n >= 0:
            aux_list = []
            for element in elements:
                index = 0
                if isinstance(element, list):
                    for value in self.clear_list:
                        if value[2] == depends:
                            depends_n+=1
                    self.append_element(element, aux_list, depends, depends_n, level)
                else:
                    element = str(element).replace(' ','_')

                    if depends=='':
                        aux_list.append({ 'id' : self.annotation_tree
                        .next_annotation_id,'annotation' : self.utterance})
                        depends = self._dependency
                        index-=1
                    else:
                        for value in self.clear_list:
                            if value[0]==element:
                                if index is 0:
                                    depends = value[2]
                                aux_list.append({ 'id' : self.annotation_tree.
                                next_annotation_id,'annotation' : value[1]})
                                self.clear_list.remove(value)
                                break
                    index+=1
                    depends_n-=1

            if len(aux_list) is not 0:
                empty_list.append(aux_list)

        if len(empty_list) is not 0:
            new_list.append(empty_list)

        if level==1:
            return new_list

    def elements_sort(self, elements, depends):
        index = 0
        restart = True
        while restart:
            restart = False
            for element in elements:
                if isinstance(element, list):
                    self.elements_sort(element, depends)
                    for value in self.elements_list:
                        if value[2]==depends:
                            restart = True
                            break
                else:
                    element = str(element).replace(' ','_')

                    for value in self.elements_list:
                        value_changed = value[0].split('-')
                        if value_changed[0]==element and depends==value[2]:
                            if index is 0:
                                depends = value[0].replace('-a','-n')
                            self.clear_list.append((element,value[1],value[2]))
                            self.elements_list.remove(value)
                            break
                    index+=1

    def generate_file(self):
        # Read header file
        doc = minidom.parse(self.filepath)

        annotation_list = []
        annotatios_files = doc.getElementsByTagName('annotation')

        # Get the files to look for
        for annotation in annotatios_files:
            loc = annotation.getAttribute('loc') # File name
            fid = annotation.getAttribute('f.id') # File id
            annotation_list.append((fid, loc))

        f = codecs.open(self.basedirname+'-graf.xml','w','utf-8')

        doc = self._create_graf_header()

        graph = doc.getElementsByTagName('graph').item(0)
        for ann in annotation_list:
            doc_parsed = minidom.parse(self.dirname+'/'+ann[1])

            doc = self._update_label_usage(doc, graph, ann[0])

            nodes = doc_parsed.getElementsByTagName('node')
            for node in nodes:
                graph.appendChild(node)

            edges = doc_parsed.getElementsByTagName('edge')
            for edge in edges:
                graph.appendChild(edge)

            regions = doc_parsed.getElementsByTagName('region')
            for region in regions:
                graph.appendChild(region)

            annotations = doc_parsed.getElementsByTagName('a')
            for a in annotations:
                graph.appendChild(a)
                self._update_label_occurs(doc, ann[0])

        raw_string = str(doc.toxml()).replace('\n','')
        raw_string = raw_string.replace('>      <','><')
        raw_string = raw_string.replace('>    <','><')
        raw_string = raw_string.replace('>  <','><')
        indent = minidom.parseString(raw_string)

        f.write(indent.toprettyxml('    '))

        f.close()

    def _update_label_usage(self, doc, graph, label):
        labelsDecl = doc.getElementsByTagName('labelsDecl').item(0)
        labelUsage = doc.createElement("labelUsage")
        labelUsage.setAttribute('label',label)
        labelUsage.setAttribute('occurs','0')
        labelsDecl.appendChild(labelUsage)

        return doc

    def _update_label_occurs(self, doc, label):
        # Update the occurs of wich label
        for node in doc.getElementsByTagName('labelUsage'):
            if node.getAttribute('label') == label:
                value = int(node.getAttribute('occurs'))
                value+=1
                node.setAttribute('occurs',str(value))
                return doc

    def _create_graf_header(self):

        doc = Document()
        graph = doc.createElement("graph")
        graph.setAttribute("xmlns", "http://www.xces.org/ns/GrAF/1.0/")
        doc.appendChild(graph)

        # Header
        graphheader = doc.createElement("graphHeader")
        labelsdecl = doc.createElement("labelsDecl")
        graphheader.appendChild(labelsdecl)
        graph.appendChild(graphheader)

        return doc
