# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

""" This document contain the responsible
methods to write and parse the GrAF files.
The parser use the ContentHandler from
SAX Xml module.
"""

from __future__ import absolute_import

import abc
import os

from xml.etree.ElementTree import tostring
from xml.dom import minidom

import graf

class Tier:
    """A list of tiers.
    The name is the tier unique identification.

    """

    __slots__ = ['name', 'annotation_space']

    def __init__(self, name, annotaion_space=None):
        self.name = name
        self.annotation_space = annotaion_space


class Annotation:
    """A list of annotations.
    The id is the annotation identification, the
    value the annotation value and the features are
    a dict type of values containing the annotation
    features.

    """

    __slots__ = ['id', 'value', 'features']

    def __init__(self, id, value, features=None):
        self.value = value
        self.id = id
        self.features = features


class NodeId:
    """A list of nodes using a specific format.
    The prefix is the node type and the index
    the identification number.

    """

    __slots__ = ['prefix', 'index']

    def __init__(self, prefix, index):
        self.prefix = prefix
        self.index = index

    def __str__(self):
        return "{0}/n{1}".format(self.prefix, self.index)

    def str_edge(self):
        return "e{0}".format(self.index)

    def str_region(self):
        return "{0}/r{1}".format(self.prefix, self.index)


class BaseParser(object):
    """This class is a base class to the
    parser classes in order to create
    GrAF objects.
    This class contains some methods that must be
    implemented other wise it will be raise a
    exception error.
    Although the methods that should be implemented
    with properly code are the get_root_tiers,
    get_child_tiers_for_tier and get_annotations_for_tier.
    The method tier_has_regions and region_for_annotation
    could simply return None or pass.

    Raises
    ------
    NotImplementedError
        Method must be implemented.

    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_root_tiers(self):
        """Method to get the root tiers. The root tiers
        are defined by the parser when the method is
         implemented.

        Returns
        -------
        list : array-like
            List of tiers type.

        """

        raise NotImplementedError("Method must be implemented")

    @abc.abstractmethod
    def get_child_tiers_for_tier(self, tier):
        """Method that get the child tiers of a specific tier.

        Parameters
        ----------
        tier : object
            Tier object.

        Returns
        -------
        list : array-like
            List of tiers type.

        See also
        --------
        Tier

        """

        raise NotImplementedError("Method must be implemented")

    @abc.abstractmethod
    def get_annotations_for_tier(self, tier, annotation_parent=None):
        """Method that get all the annotations for a specific tier.
        The annotations can be filtered using an annotation parent.

        Parameters
        ----------
        tier : object
            Tier object.
        annotation_parent : object
            Annotation object.

        Returns
        -------
        list : array-like
            List of annotations type.

        See also
        --------
        Tier, Annotation

        """

        raise NotImplementedError("Method must be implemented")

    @abc.abstractmethod
    def tier_has_regions(self, tier):
        """Method to verify if a tier has regions.

        Parameters
        ----------
        tier : object
            Tier object.

        Returns
        -------
        has_region : bool
            A true or false variable.

        See also
        --------
        Tier

        """

        raise NotImplementedError("Method must be implemented")

    @abc.abstractmethod
    def region_for_annotation(self, annotation):
        """Method to get the regions values of a specific
         annotation.

        Parameters
        ----------
        annotation : object
            Annotation object.

        Returns
        -------
        regions : tuple
            A tuple with the two regions.

        See also
        --------
        Annotation

        """

        raise NotImplementedError("Method must be implemented")


class GrAFConverter:
    """This class handles the conversion of different file formats into GrAF
    objects and back again. It uses a sub-class of BaseParser to get the
    annotations and the tier hierarchies. A sub-class of BaseWriter is used
    to write back the files. Please be aware that meta-data might get lost
    if you write to a file format from another one. This depends on whether the
    output file format can store all meta-data from the input file format.
    In any case all the data and annotation will be stored.

    """

    def __init__(self, parser, writer=None):
        self.parser = parser
        self.writer = writer
        self.graf = graf.Graph()
        self.tier_hierarchies = []
        self.meta_information = None

    def write(self, outputfile):
        if self.writer:
            self.writer.write(outputfile, self.graf, self.tier_hierarchies)

    def parse(self):
        """This method will be the responsible to transform
        the parser into a GrAF object. This method also
        retrieves the tiers hierarchies.

        """

        self._tiers_parent_list = []
        tiers_hierarchy_map = {}

        for tier in self.parser.get_root_tiers():
            self._convert_tier(tier, None, None)

        i = 0
        for t in self._tiers_parent_list:
            if t[1] is None:
                i += 1
                tiers_hierarchy_map[str(i)] = [t[0]]
            else:
                self._append_tier_to_hierarchy(tiers_hierarchy_map[str(i)], t[1], t[0])

        for i, hierarchy in tiers_hierarchy_map.items():
            self.tier_hierarchies.append(hierarchy)

        if hasattr(self.parser, 'meta_information'):
            self.meta_information = self.parser.meta_information

    def _convert_tier(self, tier, parent_node, parent_annotation, parent_prefix=None):
        child_tiers = self.parser.get_child_tiers_for_tier(tier)

        if tier.annotation_space is None:
            prefix = tier.name
            annotation_name = prefix
        else:
            annotation_name = tier.annotation_space.replace(' ', '_')

            prefix = annotation_name + "/" + tier.name

        has_regions = False

        if self.parser.tier_has_regions(tier):
            has_regions = True

        self._add_tier_in_hierarchy_list(prefix, parent_prefix)

        annotations = self.parser.get_annotations_for_tier(tier, parent_annotation)

        for annotation in annotations:
            regions = None

            if has_regions:
                regions = self.parser.region_for_annotation(annotation)

            node_id = NodeId(prefix, annotation.id)
            self._add_node(node_id, annotation, annotation_name, regions, parent_node)

            if child_tiers:
                for t in child_tiers:
                    self._convert_tier(t, node_id, annotation, prefix)

        if annotations == [] and child_tiers:
            for t in child_tiers:
                self._convert_tier(t, None, None, prefix)

    def _add_tier_in_hierarchy_list(self, prefix, parent_prefix):
        if not (prefix, parent_prefix) in self._tiers_parent_list:
            self._tiers_parent_list.append((prefix, parent_prefix))

    def _append_tier_to_hierarchy(self, tiers_list, parent_tier, tier):
        for t in tiers_list:
            if isinstance(t, list):
                self._append_tier_to_hierarchy(t, parent_tier, tier)
            else:
                if t == parent_tier:
                    tiers_list.append([tier])

    def _add_node(self, node_id, annotation, annotation_name, regions, from_node_id):
        self._add_node_to_graph(node_id, regions, from_node_id)
        self._add_graf_annotation(annotation_name, annotation.id, node_id,
                                  annotation.value, annotation.features)

    def _add_graf_annotation(self, annotation_name, annotation_id,
                             annotation_ref, annotation_value, annotation_features=None):
        annotation = graf.Annotation(annotation_name, annotation_features,
                                     annotation_id)

        if annotation_value is not None:
            annotation.features['annotation_value'] = annotation_value

        self.graf.nodes[str(annotation_ref)].annotations.add(annotation)

        if annotation_name in self.graf.annotation_spaces:
            if annotation not in self.graf.annotation_spaces[annotation_name]:
                self.graf.annotation_spaces[annotation_name].add(annotation)
        else:
            annotation_space = graf.AnnotationSpace(annotation_name)
            annotation_space.add(annotation)

            self.graf.annotation_spaces.add(annotation_space)

    def _add_node_to_graph(self, node_id, regions=None,
                           from_node_id=None):
        node = graf.Node(str(node_id))

        if from_node_id is not None:
            edge_id = node_id.str_edge()
            edge = graf.Edge(edge_id, self.graf.nodes[str(from_node_id)], node)

            self.graf.edges.add(edge)

        if regions is not None:
            region_id = node_id.str_region()
            region = graf.Region(region_id, *regions)
            node.add_region(region)

            self.graf.regions.add(region)

        self.graf.nodes.add(node)


class Writer():

    def __init__(self, **kwargs):
        self.tier_hierarchies = None
        self.meta_information = None
        self.standoffheader = graf.StandoffHeader(**kwargs)

    def _flatten_hierarchy_elements(self, elements):
        """Flat the elements appended to a new list of elements.

        Parameters
        ----------
        elements : array_like
            An array of string values.

        Returns
        -------
        flat_elements : array_like
            An array of flattened `elements`.

        """

        flat_elements = []
        for e in elements:
            if type(e) is list:
                flat_elements.extend(self._flatten_hierarchy_elements(e))
            else:
                flat_elements.append(e)
        return flat_elements

    def write(self, outputfile, graf_graph, tier_hierarchies, meta_information=None):
        """Writes the converter object as GrAF files.

        Parameters
        ----------
        outputfile : str
            The filename of the output file. The filename should be the header
            file for GrAF with the extension ".hdr".
        graf_graph : GrAF
        tier_hierarchies : array_like

        """
        (base_dir_name, _) = os.path.splitext(outputfile)

        self._get_parents(tier_hierarchies)

        standoffrenderer = graf.StandoffHeaderRenderer("{0}.hdr".format(base_dir_name))

        for tier_name in self._flatten_hierarchy_elements(
                tier_hierarchies):
            annotation_space = tier_name.split('/')[0]
            out_graf = graf.Graph()
            renderer = graf.GrafRenderer("{0}-{1}.xml".format(
                base_dir_name, annotation_space
            ))
            out_graf.nodes = [n for n in graf_graph.nodes
                              if n.id.startswith(tier_name)]
            out_graf.edges = [e for e in graf_graph.edges
                              if e.to_node.id.startswith(tier_name)]
            out_graf.regions = [r for r in graf_graph.regions
                                if r.id.startswith(tier_name)]
            out_graf.annotation_spaces.add(graf.AnnotationSpace(
                annotation_space))
            out_graf.header.add_dependency(self._parent[tier_name])

            renderer.render(out_graf)

            basename = os.path.basename(base_dir_name)
            self.standoffheader.datadesc.add_annotation("{0}-{1}.xml".
                                                        format(basename, annotation_space), annotation_space)

        standoffrenderer.render(self.standoffheader)
        self._generate_metafile(base_dir_name, meta_information)

    def _get_parents(self, tier_hierarchies):
        self._parent = {}

        for h in tier_hierarchies:
            self._get_hierarchy_parents(h, None)


    def _get_hierarchy_parents(self, hierarchy, parent):
        for i, h in enumerate(hierarchy):
            if isinstance(h, list):
                self._get_hierarchy_parents(h, parent)
            else:
                self._parent[h] = parent

                if i is 0:
                    parent = h.split('/')[0]

    def _generate_metafile(self, basedirname, meta_information = None):
        """Generate a metafile with all the extra information
        extracted from a file when it is parsed.

        Parameters
        ----------
        basedirname : str
            Base name of the inpufile.
        meta_information: ElementTree
            ElementTree with the extra information.

        """

        if meta_information:
            out = open("{0}-extinfo.xml".format(basedirname), "wb")
            doc = minidom.parseString(tostring(meta_information, encoding="utf-8"))
            out.write(doc.toprettyxml(encoding='utf-8'))
            out.close()