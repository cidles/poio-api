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

from xml.sax._exceptions import SAXParseException
from xml.dom.minidom import Document
from xml.dom import minidom
from analyzer import ProcessContent
from poioapi.io import txtrawfile
from poioapi.io import header

import codecs
import os

class Writer():

    def __init__(self, annotation_tree, header_file):
        """Class's constructor.

        Parameters
        ----------
        filepath : str
            Path of the file to manipulate.

        """

        self.filepath = header_file
        basedirname = self.filepath.split('.')
        self.basedirname = basedirname[0]
        self.header = header.CreateHeaderFile(self.filepath)
        self.level_map = []
        self.annotation_tree = annotation_tree

    def write(self):

        self.data_structure_type = self.annotation_tree.data_structure_type

        txt =  txtrawfile.CreateRawFile(self.basedirname,
            self.annotation_tree, self.data_structure_type.data_hierarchy)
        txt.create_raw_file()

        self.header.author = 'CIDLeS'
        self.header.filename = txt.filename
        self.header.primaryfile = txt.txt_file

        # Create the first annotation file
        self.header.add_annotation(txt.loc, txt.fid)

        # Map the elements in the data structure type
        self.seek_tags(self.data_structure_type.data_hierarchy, 0)

        # Verify the elements
        for element in self.annotation_tree.elements():
            self.seek_elements(element,
                self.data_structure_type.data_hierarchy, 0)

        self.header.create_header()

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
                                hierarchy_element =\
                                self.level_map[index_map-1]
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
                            self.level_map[idx] = (item[0], item[1],
                                                   new_value)
                            need_increment = False
                            break
                    need_increment = False

                index+=1

    def add_element(self, annotation, annotation_value, depends,
                    increment):

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

        if level > 2 and annotation != 'word'\
        or (annotation == 'translation' or annotation == 'comment' or annotation == 'graid2'):
            doc = self.create_dependent_node(doc, graph,
                annotation, annotation_value, depends, increment)
        else:
            doc = self.create_node_region(doc, graph, depends, annotation,
                annotation_value, increment, filepath)

        # Indent the xml file
        raw_string = str(doc.toxml()).replace('\n','')
        raw_string = raw_string.replace('>      <','><')
        raw_string = raw_string.replace('>    <','><')
        raw_string = raw_string.replace('>  <','><')
        indent = minidom.parseString(raw_string)

        if new_file:
            # Write the content in XML file
            f.write(indent.toprettyxml('  '))

            #Close XML file
            f.close()
        else:
            file = codecs.open(filepath,'w', 'utf-8')

            file.write(indent.toprettyxml('  '))

            file.close()

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

        # Creating the link node
        link = doc.createElement("link")
        link.setAttribute("targets", annotation + "-r"
        + str(increment)) # ref
        node.appendChild(link)

        graph.appendChild(node)

        # Creating the edge node
        edge = doc.createElement("edge")
        edge.setAttribute("xml:id", annotation + "-e"
        + str(seg_count)) # edge id
        edge.setAttribute("from", depends + "-n"
        + str(increment)) # from node
        edge.setAttribute("to", annotation + "-n"
        + str(seg_count)) # to node

        graph.appendChild(edge)

        region = doc.createElement("region")
        region.setAttribute("xml:id", annotation + "-r"
        + str(seg_count)) # Region
        region.setAttribute("anchors",
            str(counter) + " " +
            str(last_counter)) # Anchors

        graph.appendChild(region)

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

    def load_as_tree(self, data_hierarchy):
        # Read header file
        doc_header = minidom.parse(self.filepath)

        files_list = []
        annotatios_files = doc_header.getElementsByTagName('annotation')

        # Get the files to look for
        for annotation in annotatios_files:
            loc = annotation.getAttribute('loc') # File name
            fid = annotation.getAttribute('f.id') # File id
            files_list.append((fid, loc))

        tokens_list = []
        features_list = []

        self.seek_tags(data_hierarchy, 0)

        for file in files_list:
            procContent = ProcessContent(self.basedir+'/'+file[1])
            procContent.process()

            features_map = procContent.get_features_map()
            tokens_map = procContent.get_tokens_map()

            features_list.append(features_map)
            tokens_list.append(tokens_map)

        flatten_tokens_list = []
        flatten_features_list = []
        self.elements_list = []

        for tokens in tokens_list:
            for token in tokens:
                flatten_tokens_list.append(token)

        for features in features_list:
            for feature in features:
                flatten_features_list.append(feature)
                self.elements_list.append(feature)

        self.clear_list = []
        self.final_list = []
        self.dive_into(data_hierarchy, 'utterance-n0')

        self.final_list.append(self.create_element(data_hierarchy, []))
        print(self.final_list)

    def create_element(self, elements, new_list):
        restart = True
        while restart:
            restart = False
            for element in elements:
                if isinstance(element, list):
                    new_list.append([self.create_element(element, [])])
                    for value in self.clear_list:
                        if value[0]==element[0]:
                            restart = True
                            break
                    if restart:
                        print('toma')
                        break
                else:
                    element = str(element).replace(' ','_')
                    for value in self.clear_list:
                        if value[0]==element:
                            new_list.append(value[1])
                            self.clear_list.remove(value)
                            break

            return new_list

    def dive_into(self, elements, depends):
        index = 0
        restart = True
        while restart:
            restart = False
            for element in elements:
                if isinstance(element, list):
                    self.dive_into(element, depends)
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
                                #print(str(element) + ' --- ' + str(value[1]))
                            self.clear_list.append((element,value[1]))
                            self.elements_list.remove(value)
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
            doc_parsed = minidom.parse(self.basedir+'/'+ann[1])

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

    def seek_tags(self, hierarchy, level):
        level+=1
        for index in range(len(hierarchy)):
            if isinstance(hierarchy[index],list):
                self.seek_tags(hierarchy[index], level)
            else:
                level_list = (level,
                              hierarchy[index].replace(' ','_'), 0)
                self.level_map.append(level_list)
