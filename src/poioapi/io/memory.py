# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2014 Poio Project
# Author: Peter Bouda <pbouda@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

"""
This modules provides classes to store informations from Parsers to a data
structure in memors. The data that is stored is equivalent to a GrAF graph but
without the overhead of Python objects. The AnnotationGraph object thus can be
used wit memory or GrAF data storage.

"""

import redis

class MemoryConverter:
    """This class handles the conversion of different file formats into memory
    data types. It uses a sub-class of BaseParser to get the
    annotations and the tier hierarchies.

    """

    def __init__(self, parser, writer=None):
        self.parser = parser
        self.tier_hierarchies = []
        self.meta_information = None
        self.primary_data = None
        self.original_file = None
        self.annotations_for_parent = dict()
        self.region_for_annotation = dict()

    def parse(self):
        """This method will be the responsible to transform
        the parser into a redis key/value items. This method also
        retrieves and stores the tiers hierarchies.

        """

        self._tiers_parent_list = []
        self.root_tiers = []
        tiers_hierarchy_map = {}

        for tier in self.parser.get_root_tiers():
            self.root_tiers.append(tier.name)
            self._convert_tier(tier, None)

        i = 0
        for t in self._tiers_parent_list:
            if t[1] is None:
                i += 1
                tiers_hierarchy_map[str(i)] = [t[0]]
            else:
                self._append_tier_to_hierarchy(tiers_hierarchy_map[str(i)],
                    t[1], t[0])

        for i, hierarchy in tiers_hierarchy_map.items():
            self.tier_hierarchies.append(hierarchy)

        if hasattr(self.parser, 'meta_information'):
            self.meta_information = self.parser.meta_information

        self.primary_data = self.parser.get_primary_data()
        if hasattr(self.parser, 'filepath') and \
                isinstance(self.parser.filepath, str):
            self.original_file = os.path.abspath(self.parser.filepath)

    def _convert_tier(self, tier, parent_annotation,
            parent_prefix=None):
        child_tiers = self.parser.get_child_tiers_for_tier(tier)

        if tier.annotation_space is None:
            prefix = tier.name
            annotation_name = prefix
        else:
            annotation_name = tier.annotation_space.replace(' ', '_')

            prefix = "{0}{1}{2}".format(annotation_name, GRAFSEPARATOR,
                tier.name)

        has_regions = False

        if self.parser.tier_has_regions(tier):
            has_regions = True

        self._add_tier_in_hierarchy_list(prefix, parent_prefix)

        annotations = self.parser.get_annotations_for_tier(tier,
            parent_annotation)

        for annotation in annotations:
            region = None

            if has_regions:
                region = self.parser.region_for_annotation(annotation)
                self.region_for_annotation[annotation.id] = region

            #node_id = NodeId(prefix, annotation.id)
            parent_annotation_id = None
            if parent_annotation is not None:
                parent_annotation_id = parent_annotation.id
            self.annotations_for_parent[(parent_annotation_id, tier.name)] = \
                annotation
            #self._add_node(node_id, annotation, annotation_name, regions,
            #    parent_node)
            #self._add_root_nodes(prefix, node_id)

            if child_tiers:
                for t in child_tiers:
                    self._convert_tier(t, annotation, prefix)

        if annotations == [] and child_tiers:
            for t in child_tiers:
                self._convert_tier(t, None, prefix)

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

    # def _add_node(self, node_id, annotation, annotation_name, regions,
    #         from_node_id):
    #     self._add_node_to_graph(node_id, regions, from_node_id)
    #     self._add_graf_annotation(annotation_name, annotation.id, node_id,
    #                               annotation.value, annotation.features)

    # def _add_root_nodes(self, prefix, node_id):
    #     if prefix in self.root_tiers:
    #         self.graf.header.roots.append(node_id.to_str())

    # def _add_graf_annotation(self, annotation_name, annotation_id,
    #         annotation_ref, annotation_value, annotation_features=None):
    #     annotation = graf.Annotation(annotation_name, annotation_features,
    #                                  annotation_id)

    #     if annotation_value is not None:
    #         annotation.features['annotation_value'] = annotation_value

    #     self.graf.nodes[annotation_ref.to_str()].annotations.add(annotation)

    #     if annotation_name in self.graf.annotation_spaces:
    #         #if annotation not in self.graf.annotation_spaces[annotation_name]:
    #         self.graf.annotation_spaces[annotation_name].add(annotation)
    #     else:
    #         annotation_space = graf.AnnotationSpace(annotation_name)
    #         annotation_space.add(annotation)

    #         self.graf.annotation_spaces.add(annotation_space)

    # def _add_node_to_graph(self, node_id, regions=None,
    #                        from_node_id=None):

    #     node = graf.Node(node_id.to_str())

    #     if from_node_id is not None:
    #         edge_id = node_id.str_edge()
    #         self.graf.create_edge(self.graf.nodes[from_node_id.to_str()], node,
    #             edge_id)

    #     if regions is not None:
    #         region_id = node_id.str_region()
    #         region = graf.Region(region_id, *regions)
    #         node.add_region(region)

    #         self.graf.regions.add(region)

    #     self.graf.nodes.add(node)
