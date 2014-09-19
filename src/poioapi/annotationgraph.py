# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: Peter Bouda <pbouda@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

from __future__ import absolute_import, unicode_literals

import sys
import os.path
import re
import codecs

from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

import poioapi.io.elan
import poioapi.io.mandinka
import poioapi.io.obt
import poioapi.io.graf
import poioapi.io.toolbox
import poioapi.io.toolboxxml
import poioapi.io.shoebox
import poioapi.io.typecraft

import poioapi.data
import poioapi.mapper

import graf

class AnnotationGraph():
    """This class stores annotation data as annotation graphs and makes it
    accessible in tier hierarchies. It reads data from various file formats.

    """

    def __init__(self, data_structure_type = None):
        if data_structure_type is None:
            self.structure_type_handler = None
        elif isinstance(data_structure_type, poioapi.data.DataStructureType):
            self.structure_type_handler = data_structure_type
        else:
            raise(
                poioapi.data.DataStructureTypeNotSupportedError(
                    "Data structure type {0} not supported".format(
                        data_structure_type)))

        self.graf = None
        self.tier_hierarchies = None
        self.meta_information = None
        self.root_tiers = []
        self.primary_data = None
        self.source_type = None

        self.filters = []
        self.filtered_node_ids = []

        self.tier_mapper = poioapi.mapper.TierMapper()

    @classmethod
    def from_elan(cls, stream):
        """This method generates a GrAF object
        from a Elan file.

        """
        return cls._from_file(stream, poioapi.data.EAF)

    @classmethod
    def from_mandinka(cls, stream, tier_map_file_path=''):
        """This method generates a GrAF object
        from a Elan file.

        """
        cls.tier_mapper = poioapi.io.mandinka.tier_mapping()
        return cls._from_file(stream, poioapi.data.MANDINKA, tier_map_file_path=tier_map_file_path)

    @classmethod
    def from_obt(cls, stream):
        """This method generates a GrAF object
        from a Elan file.

        """
        return cls._from_file(stream, poioapi.data.OBT)

    @classmethod
    def from_typecraft(cls, stream):
        """This method generates a GrAF object
        from a Typecraft file.

        """
        return cls._from_file(stream, poioapi.data.TYPECRAFT)

    @classmethod
    def from_shoebox(cls, stream):
        """This method generates a GrAF object
        from a shoebox file.

        """
        return cls._from_file(stream, poioapi.data.SHOEBOX)

    @classmethod
    def from_toolboxxml(cls, stream):
        """This method generates a GrAF object
        from a xml toolbox file.

        """
        return cls._from_file(stream, poioapi.data.TOOLBOXXML)

    @classmethod
    def from_toolbox(cls, stream, tier_map_file_path=''):
        """This method generates a GrAF object
        from a xml toolbox file.

        """
        cls.tier_mapper = poioapi.io.toolbox.tier_mapping()
        return cls._from_file(stream, poioapi.data.TOOLBOX, tier_map_file_path=tier_map_file_path)

    @classmethod
    def from_graf(cls, stream):
        """Load the project annotation graph from a GrAF/XML file or stream.

        Parameters
        ----------
        stream : str or io.stream
            The path to a GrAF/XML file.

        """
        ag = cls()
        if not hasattr(stream, 'read'):
            stream = ag._open_file_(stream)

        parser = graf.GraphParser()
        ag.graf = parser.parse(stream)
        ag.from_file_type = poioapi.data.GRAF

        return ag

    def _open_file_(self, filename):
        if sys.version_info[:2] < (3, 0):
            return codecs.open(filename, "rb")

        return codecs.open(filename, "r", "utf-8")

    @classmethod
    def _from_file(cls, stream, stream_type, tier_labels_file_path='', **kwargs):
        ag = cls()

        #load aditional tier labels if supplied
        if tier_labels_file_path != '' and tier_labels_file_path is not None:
            ag.tier_mapper.load_mapping(tier_labels_file_path)

        # TODO: move the stream opening to the parser classes
        if stream_type != poioapi.data.TOOLBOX and \
                stream_type != poioapi.data.MANDINKA:
            if not hasattr(stream, 'read'):
                stream = ag._open_file_(stream)

        parser = None
        if stream_type == poioapi.data.EAF:
            parser = poioapi.io.elan.Parser(stream)
        elif stream_type == poioapi.data.MANDINKA:
            if not hasattr(stream, 'read'):
                stream = codecs.open(stream, "rb")
            parser = poioapi.io.mandinka.Parser(stream, tier_label_map=ag.tier_mapper)
        elif stream_type == poioapi.data.OBT:
            parser = poioapi.io.obt.Parser(stream)
        elif stream_type == poioapi.data.TYPECRAFT:
            parser = poioapi.io.typecraft.Parser(stream)
        elif stream_type == poioapi.data.TOOLBOXXML:
            parser = poioapi.io.toolboxxml.Parser(stream)
        elif stream_type == poioapi.data.SHOEBOX:
            parser = poioapi.io.shoebox.Parser(stream)
        elif stream_type == poioapi.data.TOOLBOX:
            if not hasattr(stream, 'read'):
                stream = codecs.open(stream, "rb")
            parser = poioapi.io.toolbox.Parser(stream, mapper=ag.tier_mapper)

        converter = poioapi.io.graf.GrAFConverter(parser)
        converter.parse()

        ag.tier_hierarchies = converter.tier_hierarchies
        ag.meta_information = converter.meta_information
        ag.root_tiers = converter.root_tiers
        ag.graf = converter.graf
        ag.primary_data = converter.primary_data

        ag.source_type = stream_type

        # set the first tier hierarchy as the default data_structure_type
        ag.structure_type_handler = \
            poioapi.data.DataStructureType(ag.tier_hierarchies[0])

        return ag


    ########################################################## Methods

    def root_nodes(self):
        """Retrieve the root nodes from the annotation graph. Root nodes are
        the nodes that have a label that is the root node of the data structure
        type as the root node. The root nodes are order by the "start" value
        of their region.

        Returns
        -------
        root_nodes : list of graf.Node
            Return root nodes of the graph.

        """

        res = list()
        base_tier_name = self.structure_type_handler.flat_data_hierarchy[0]
        res = self.nodes_for_tier(base_tier_name)

        try:
            return sorted(res, key=lambda node: node.links[0][0].start)
        except IndexError as indexError:
            return res

    def nodes_for_tier(self, tier_name, parent_node = None):
        """Retreive all nodes for a given tier name. The parameter
        tier_name specifies the type if the neighbours. For example if
        the parent node is an utterance the tier name "word" specifies that
        all "word" nodes that are connected to the utterance node should
        be returned. The tier name must be a children of the parent node's
        type in the data hierarchy.

        Parameters
        ----------
        tier_name : str
            The label of the neighbour nodes to search.
        parent_node : graf.Node
            The ID of the node to start the search.

        Returns
        -------
        nodes : list of graf.Node

        """
        #node = self.graf.nodes[node_id]
        res = []
        if parent_node:
            for target_node in parent_node.iter_children():
                if target_node.id.startswith(tier_name + poioapi.io.graf.GRAFSEPARATOR):
                    res.append(target_node)
        else:
            if tier_name in self.root_tiers:
                for target_node_id in self.graf.header.roots:
                    n = self.graf.nodes[target_node_id]
                    if n.id.startswith(tier_name + poioapi.io.graf.GRAFSEPARATOR):
                        res.append(self.graf.nodes[target_node_id])
            if len(res) == 0:
                for target_node in self.graf.nodes:
                    if target_node.id.startswith(tier_name + poioapi.io.graf.GRAFSEPARATOR):
                        res.append(target_node)
        return res

    def annotations_for_tier(self, tier_name, node=None):
        """Return all annotations of the given node that belong to the given
        tier name. The tier name is matched with the `label` of the
        annotations.

        Parameters
        ----------
        tier_name : str
            The label to search for in the annotations.
        node : graf.Node
            The node that has annotation to search.

        Returns
        -------
        annotations : list of graf.Annotation

        """
        res = []

        if node is not None and node.id.startswith(tier_name):
            for a in node.annotations:
                res.append(a)
        else:
            nodes = self.nodes_for_tier(tier_name, node)
            for n in nodes:
                for a in n.annotations:
                    res.append(a)

        return res

    def annotation_value_for_annotation(self, annotation):
        """Returns the annotation value for a given annotation.

        Parameters
        ----------
        annotation: graf.Annotation
            The annotation to get the value for.

        Returns
        -------
        annotation_value : str
            The annotation value.
        """
        annotation_value = ""
        try:
            annotation_value = annotation.features.get_value("annotation_value")
        except KeyError:
            pass
        
        return annotation_value

    def annotation_value_for_node(self, node):
        """Returns the annotation value for a given node. If the node has
        more then one annotation, then only the first annotation value is
        returned.

        Parameters
        ----------
        node : graf.Node
            The node to return the annotation values for.

        Returns
        -------
        annotation_value : str
            The annotation value.

        """
        return self.annotation_value_for_annotation(
            node.annotations.get_first())

    def as_html_table(self, filtered = False, full_html = True):
        """Return the graph as a HTML table.

        Parameters
        ----------
        filtered : bool
            Whether to us the filtered graph or the full graph.
        full_html: bool
            Whether to return a complete HTML page (i.e. with "<html>" etc.)
            or just the <table> element.

        Returns
        -------
        html = str
            The HTML for the GrAF graph.

        """
        html = ""
        if full_html:
            html = "<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" /></head><body>\n"

        for i, root_node in enumerate(self.root_nodes()):
            if filtered and (len(self.filtered_node_ids) == 0 or \
                    root_node.id not in self.filtered_node_ids[-1]):
                continue

            html += "<table style=\"border-collapse:collapse;border:1px solid black;margin-bottom:20px;\">"
            html += "<tr><td style=\"padding:4px;border:1px solid black;\">{0}</td>".format(i)
            html += "<td style=\"border:1px solid black;\">"

            html += self._node_as_html_table(
                root_node, self.structure_type_handler.data_hierarchy)

            html += "</td></tr></table>"

        if full_html:
            html += "</body></html>"

        return html

    def _node_as_html_table(self, node, hierarchy):
        """Create an html table for a node.

        Parameters
        ----------
        node : array_like
            The root node to start the traversal.
        hierarchy: array_like
            An array with the data structure hierarchy.

        Returns
        -------
        html : str
            An html table of the node.

        """

        table = "<table style=\"margin:0;padding:0;float:left;border-collapse:collapse;\">"

        inserted = 0

        for i, t in enumerate(hierarchy):

            table += "<tr style=\"margin:0;padding:0;\">"

            if type(t) is list:
                table += "<td style=\"margin:0;padding:0px;\">"
                node_list = self.nodes_for_tier(t[0], node)
                for i, n in enumerate(node_list):
                    table += self._node_as_html_table(n, t)

                table += "</td>"
            else:
                #row = self.structure_type_handler.flat_data_hierarchy.index(t)

                a_list = self.annotations_for_tier(t, node)
                a = ""
                if len(a_list) > 0:
                    a = self.annotation_value_for_annotation(a_list[0])
                if a == "":
                    a = "&nbsp;"

                #if column in table[row]:
                #    table[row][column] = (a, table[row][column][1])
                #else:
                #    table[row][column] = (a, 1)
                table += "<td style=\"margin:0;padding:3px;\">{0}</td>".format(a)

            table += "</tr>"

        table += "</table>"
        return table

    def to_elan(self, outputfile):
        """Write the annotation graph as Elan EAF files.
        """
        converter = poioapi.io.graf.GrAFConverter(
            None, poioapi.io.elan.Writer())
        converter.graf = self.graf
        converter.tier_hierarchies = self.tier_hierarchies
        converter.meta_information = self.meta_information
        converter.write(outputfile)

    def to_graf(self, outputfile):
        """Write the annotation graph as GrAX/XML files.
        
        Parameters
        ----------
        outputfile : str or io stream
            The path to the output file. This filename is the header file of the
            GrAF/XML files, it should have the extension ".hdr".

        """
        converter = poioapi.io.graf.GrAFConverter(
            None, poioapi.io.graf.Writer())
        converter.graf = self.graf
        converter.tier_hierarchies = self.tier_hierarchies
        converter.meta_information = self.meta_information
        converter.write(outputfile)

    def generate_graf_files(self, inputfile, outputfile):
        """This method will create the GrAF Xml files.
        But first is need to create the GrAF object in
        order to get the values.
        In some specific cases this method will also
        create a metafile that will gathered all the
        data information to recreate a file. Elan type
        is one of those specific files and this metafile
        will garante that the extra information from the
        files like the data structure hierarchy,
        the vocabulary, the media descriptor and etc,
        will be stored. The header file it's created too.

        Parameters
        ----------
        inputfile : str
            Name of the file to generate the files.
        outputfile: str
            Name to the files generated by the method.

        """

        graf_xml_writer = poioapi.io.graf.Writer()
        graf_xml_writer.generate_graf_files(self.graf, inputfile)

        (filename, file_extension) = os.path.splitext(outputfile)

        if file_extension == ".eaf":
            self._generate_metafile(filename, self.graf)

    def _generate_metafile(self, filename, graf):
        """ This method will create a metafile
        from the original file.

        """

        (basedirname, _) = os.path.splitext(filename)

        tree = self.graf.additional_information['extra_info']

        # Generate the metadata file
        element_tree = Element('metadata')
        header_tag = SubElement(element_tree, 'header')
        tier_mapping = SubElement(header_tag, 'tier_mapping')

        for linguistic_type in tree.findall('LINGUISTIC_TYPE'):
            linguistic_type_id = linguistic_type.attrib['LINGUISTIC_TYPE_ID']

            name = linguistic_type_id.replace(' ', '_')

            type = SubElement(tier_mapping, 'type', {'name': name})

            for tier_ref in tree.findall("TIER"):
                if tier_ref.attrib["LINGUISTIC_TYPE_REF"] == linguistic_type_id:
                    SubElement(type, 'tier').text = tier_ref.attrib['TIER_ID']

        miscellaneous = SubElement(element_tree, "miscellaneous")
        SubElement(miscellaneous, tree.tag, tree.attrib)

        for child in tree:
            parent = SubElement(miscellaneous, child.tag, child.attrib)
            for lower_child in child:
                if lower_child.tag != "ANNOTATION":
                    child_element = SubElement(parent, lower_child.tag,
                        lower_child.attrib)
                    if not str(lower_child.text).isspace() or\
                       lower_child.text is not None:
                        child_element.text = lower_child.text

        filename = basedirname + "-extinfo.xml"
        file = open(filename, 'wb')
        doc = minidom.parseString(tostring(element_tree))
        file.write(doc.toprettyxml(indent='  ', encoding='utf-8'))
        file.close()

    def append_filter(self, filter):
        """Append a filter to the search.

        Parameters
        ----------
        filter : str
            Value to set the fiter.

        """

        self.filters.append(filter)

        new_filtered_elements = \
            [ node.id
            for node in self.root_nodes()
                if (len(self.filtered_node_ids) == 0 or \
                    node.id in self.filtered_node_ids[-1]) and \
                    filter.element_passes_filter(node)]

        self.filtered_node_ids.append(new_filtered_elements)

    def last_filter(self):
        """Return the latest added filter.

        Returns
        -------
        filters = array_like
            An array with the filters.
        AnnotationTreeFilter : class
            Return the class AnnotationTreeFilter.

        """

        if len(self.filters) > 0:
            return self.filters[-1]
        else:
            return AnnotationGraphFilter(self)

    def update_last_filter(self, filter):
        """Update the last filter added.

        Parameters
        ----------
        filter : str
            Value to set the fiter.

        """

        self.pop_filter()
        self.append_filter(filter)

    def pop_filter(self):
        """Remove and return item at index.

        Returns
        -------
        filter : AnnotationGraphFilter
            Last filter in self.filters.

        """

        if len(self.filters) > 0:
            self.filtered_node_ids.pop()
            return self.filters.pop()
        return None

    def init_filters(self):
        """Initialize the filters array.

        """

        self.filters = []
        self.filtered_node_ids = []

    def reset_filters(self):
        """Reset the filters array.

        """

        self.filtered_node_ids = []

        for filter in self.filters:
            new_filtered_elements = []
            for node in self.root_nodes():
                if (len(self.filtered_node_ids) == 0 or \
                        node.id in self.filtered_node_ids[-1]) and \
                        filter.element_passes_filter(node):
                    new_filtered_elements.append(node.id)

            self.filtered_node_ids.append(new_filtered_elements)

    def create_filter_for_dict(self, search_dict):
        """Creates a filter based on a give dict. The keys of the dict are
        matched against the data structure hierarchy. Only for those fields
        that are part of the data structure there will be a search term
        added to the filter. The search term is the value in the dict.

        Parameters
        ----------
        search_dict : dict
            Dictionary with search terms for different tiers.

        Returns
        -------
        filter : AnnotationGraphFilter
            A new annotation graph filter.
        """

        filter = AnnotationGraphFilter(self)
        for k in search_dict:
            if k in self.structure_type_handler.flat_data_hierarchy:
                filter.set_filter_for_tier(k, search_dict[k])
        return filter


class AnnotationGraphFilter():
    """
    AnnotationGraphFilter tree-like structure constructor.

    The main objective of this class is to make it possible
    to make searches in the a GrAF object.

    """

    (AND, OR)  = range(2)

    def __init__(self, annotation_graph):
        """Class constructor.

        """

        self.annotation_graph = annotation_graph

        self.filter = dict()
        for e in self.annotation_graph.structure_type_handler.flat_data_hierarchy:
            self.filter[e] = ""

        self.reset_match_object()
        self.inverted = False
        self.boolean_operation = self.AND
        self.contained_matches = False

    def reset_match_object(self):
        """Reset a match object.

        """

        self.matchobject = dict()
        for e in self.annotation_graph.structure_type_handler.flat_data_hierarchy:
            self.matchobject[e] = dict()

    def set_filter_for_tier(self, ann_type, filter_string):
        """Set a filter for a given type.

        Parameters
        ----------
        ann_type : str
            Value of the field in the data structure hierarchy, the tier name.
        filter_string : str
            String of the filter.

        """

        self.filter[ann_type] = filter_string

    def element_passes_filter(self, node):
        """Verify if a specific element passes in through a filter.

        Parameters
        ----------
        node : graf.Node
            The start node for the search.

        Returns
        -------
        passed : bool
            Passes or not.

        See also
        --------
        _passes_filter

        """

        # is there a filter defined?
        all_filter_empty = True
        result_dict = {}
        for ann_type in self.filter:
            if self.filter[ann_type] != "":
                all_filter_empty = False
            result_dict[ann_type] = False

        if all_filter_empty:
            return True

        self._passes_filter(
            result_dict, node,
            self.annotation_graph.structure_type_handler.data_hierarchy)

        if self.boolean_operation == self.AND:
            passed = True
        else:
            passed = False

        for ann_type in self.filter:
            if self.boolean_operation == self.AND:
                passed = (passed and result_dict[ann_type])
            else:
                passed = (passed or result_dict[ann_type])

        if self.inverted:
            passed = not passed

        return passed

    def _passes_filter(self, result_dict, node, hierarchy):
        """Verify if a specific element passes in through a filter.

        Parameters
        ----------
        passed : bool
            Passes or not.
        node : graf.Node
            The start node for the search.
        hirerarchy : list of lists
            The hierarchical data structure for the search.

        Returns
        -------
        passed : bool
            Passes or not.

        """

        for i, t in enumerate(hierarchy):
            if type(t) is list:
                local_passes = False
                node_list = self.annotation_graph.nodes_for_tier(t[0], node)
                for i, n in enumerate(node_list):
                    self._passes_filter(result_dict, n, t)

            else:
                a_list = self.annotation_graph.annotations_for_tier(t, node)
                if self.filter[t] != "":
                    if len(a_list) > 0:
                        a = self.annotation_graph.annotation_value_for_annotation(a_list[0])
                        match = re.search(self.filter[t], a)
                        if match:
                            self.matchobject[t][node.id] =\
                            [ [m.start(), m.end()] for m in re.finditer(
                                self.filter[t], a) ]
                            result_dict[t] = True
                else:
                    result_dict[t] = True
