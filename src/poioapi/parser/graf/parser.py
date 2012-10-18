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
from poioapi import annotationtree
from poioapi import data
from xmltoanntree import ProcessContent
from xml.dom.minidom import Document
from xml.dom import minidom

import pickle
import codecs

class GrafParser():

    def parsing(self):
        # Initialize the variable
        self.data_structure_type = data.DataStructureTypeGraid()

        annotation_tree = annotationtree.AnnotationTree(self.data_structure_type.data_hierarchy)

        # Open the file
        file = open('/home/alopes/tests/pi_2.pickle', "rb")
        annotation_tree.tree = pickle.load(file)

        # Verify the elements
        for element in annotation_tree.elements():
            self.seek_elements(element, self.data_structure_type.data_hierarchy, '')

        #self.add_element_xml('ann','ann_value','depends_b')
        #self.seektags(self.data_structure_type.data_hierarchy, 0)

    def seektags(self, hierarchy, level):
        index = 0
        for index in range(len(hierarchy)):
            if isinstance(hierarchy[index],list):
                self.seektags(hierarchy[index], level)
            else:
                level+=1
                print('Level ' + str(level) + ' : ' + str(hierarchy[index]))

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
                #print(str(label[index]) + ' : ' +
                #      str(element[index].get('annotation') + ' depends: ' + str(depends_on)))
                self.add_element_xml(label[index],
                    element[index].get('annotation'), depends_on)


    def add_element_xml(self, annotation, annotation_value, depends):

        # See if the file exist
        # First see if the header is created and then do the rest
        # If the depends is '' nothing don't create the depends
        # Need a way to keep the track about the id

        filepath = '/home/alopes/tests/OHHH-' + annotation +'.xml'
        new_file = False

        try:
            with open(filepath) as f:
                doc = minidom.parse(filepath)
        except IOError as e:
            f = codecs.open(filepath,'w','utf-8')
            new_file = True

        if new_file:
            doc = self.create_graf_header(annotation, depends)

        graph = doc.getElementsByTagName('graph').item(0)

        id_counter = len(doc.getElementsByTagName('a')) + 1

        if depends != '':
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
        else:
            try:
                procContent = ProcessContent(filepath)
                procContent.process()
                ranges = procContent.get_tokenizer()

                index = len(ranges) - 1
                range = ranges[index]
                range[1]

                last_counter = int(range[1])
            except SAXParseException as sax_error:
                last_counter = 0

            counter = last_counter

            last_counter += len(annotation_value)

            seg_count = len(doc.getElementsByTagName('region')) + 1

            region = doc.createElement("region")
            region.setAttribute("xml:id", annotation + "-r"
            + str(seg_count)) # Region
            region.setAttribute("anchors",
                str(counter) + " " +
                str(last_counter)) # Anchors

            graph.appendChild(region)

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

GrafParser().parsing()