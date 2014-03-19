# -*- coding: utf-8 -*-
#
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

import collections

import xml.etree.ElementTree as ET

from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

import poioapi.io.graf


class ElanTier(poioapi.io.graf.Tier):
    __slots__ = ["linguistic_type"]

    def __init__(self, name, linguistic_type):
        self.name = name
        self.linguistic_type = linguistic_type
        self.annotation_space = linguistic_type


class Parser(poioapi.io.graf.BaseParser):
    """
    Class that will handle parse Elan files.

    """

    def __init__(self, filepath):
        """Class's constructor.

        Parameters
        ----------
        filepath : str
            Path of the elan file.

        """

        self.filepath = filepath
        self._parse()

    def _parse(self):
        """This helper method does the EAF file parsing and intializes some
        internal attributes.

        """

        # With the python 2.x the element tree the strings
        # are somehow mixed with "str" and "unicode" types.
        # http://stackoverflow.com/questions/3418262/python-unicode-and-elementtree-parse
        self.root = ET.parse(self.filepath)
        self.tree = self.root.getroot()
        self.time_order = self._map_time_slots()
        self._annotations_for_parent = collections.defaultdict(list)
        self.regions_map = {}
        self.regions_cache = {}
        self.meta_information = self._retrieve_aditional_information()
        self._build_annotations()

    def get_root_tiers(self):
        """This method retrieves all the root tiers.
        In this case the root tiers are all those
        that doesn't contain "PARENT_REF".

        Returns
        -------
        list : array-like
            List of tiers type.

        """

        return [ElanTier(
                    tier.attrib['TIER_ID'], tier.attrib['LINGUISTIC_TYPE_REF'])
                for tier in self.tree.findall('TIER')
                if not 'PARENT_REF' in tier.attrib]

    def get_child_tiers_for_tier(self, tier):
        """This method retrieves all the child tiers
        of a specific tier. The children of a tier
        are all the "TIERS" that has the "PARENT_REF"
        equal to the specific tier name.

        Parameters
        ----------
        tier : object
            Tier to find the children from.

        Returns
        -------
        child_tiers : array-like
            List of tiers type.

        """

        return [ElanTier(t.attrib['TIER_ID'], t.attrib['LINGUISTIC_TYPE_REF'])
                for t in self.tree.findall("TIER")
                if "PARENT_REF" in t.attrib and
                   t.attrib["PARENT_REF"] == tier.name]

    def get_annotations_for_tier(self, tier, annotation_parent=None):
        """This method retrieves all the annotations
        of a specific tier. In elan type files there
        are two different types of annotations,
        ANNOTATION_REF and ALIGNABLE_ANNOTATION. For
        the ANNOTATION_REF the annotation_parent it's
        specified in the attribute "ANNOTATION_REF".
        As for the ALIGNABLE_ANNOTATION in order to
        use the annotation_parent it's necessary to
        try to match if the ranges of theirs
        "TIME_SLOT_REF".

        Parameters
        ----------
        tier : object
            Tier to find the annotations.
        annotation_parent : object
            Annotation parent it is the reference.

        Returns
        -------
        annotations : array-like
            List of annotations type.

        """

        parent_id = None
        if annotation_parent:
            parent_id = annotation_parent.id
        return self._annotations_for_parent[(parent_id, tier.name)]


    def _build_annotations(self):
        for t in self.tree.findall("TIER"):
            tier = ElanTier(
                t.attrib['TIER_ID'], t.attrib['LINGUISTIC_TYPE_REF'])
            self.regions_cache[tier.name] = dict()
            for a in t.findall("ANNOTATION/*"):
                annotation_id = a.attrib['ANNOTATION_ID']
                annotation_value = a.find('ANNOTATION_VALUE').text
                features = {}

                parent_annotation_id = None

                if a.tag == "ALIGNABLE_ANNOTATION":
                    ts1 = a.attrib['TIME_SLOT_REF1']
                    ts2 = a.attrib['TIME_SLOT_REF2']

                    self.regions_cache[tier.name][(
                        self.time_order[ts1], self.time_order[ts2])] = a 
                    
                    self.regions_map[annotation_id] = \
                        {'time_slot1': ts1,
                         'time_slot2': ts2}
                    if 'PARENT_REF' in t.attrib:
                        parent = self._annotation_for_region(
                            t.attrib['PARENT_REF'],
                            self.time_order[ts1],
                            self.time_order[ts2])

                        if parent is not None:
                            parent_annotation_id = parent.attrib['ANNOTATION_ID']
                else:
                    parent_annotation_id = a.attrib["ANNOTATION_REF"]
                    for attribute in a.attrib:
                        if attribute != 'ANNOTATION_REF' and \
                                attribute != 'ANNOTATION_ID' and \
                                attribute != 'ANNOTATION_VALUE' and \
                                attribute != 'PREVIOUS_ANNOTATION':
                            features[attribute] = annotation.attrib[attribute]

                self._annotations_for_parent[(
                    parent_annotation_id, t.attrib['TIER_ID'])].\
                    append(poioapi.io.graf.Annotation(
                        annotation_id, annotation_value, features))

    def _annotation_for_region(self, tier_name, start, end):
        if tier_name in self.regions_cache:
            for s, e in self.regions_cache[tier_name]:
                if s <= start and e >= end:
                    return self.regions_cache[tier_name][(s, e)]
        else:
            for t in self.tree.findall("TIER"):
                if t.attrib['TIER_ID'] == tier_name:
                    for a in t.findall("ANNOTATION/*"):
                        annotation_regions = \
                            [self.time_order[a.attrib['TIME_SLOT_REF1']],
                             self.time_order[a.attrib['TIME_SLOT_REF2']]]
                        if annotation_regions[0] <= start and \
                                annotation_regions[1] >= end:
                            return a
        return None

    def region_for_annotation(self, annotation):
        """This method retrieves the region for a
        specific annotation. The region are obtained
        through the time slots references.

        Parameters
        ----------
        annotation : object
            Annotation to get the region.

        Returns
        -------
        region : tuple
            Region of an annotation.

        """

        time_slot1 = self.regions_map[annotation.id]["time_slot1"]
        time_slot2 = self.regions_map[annotation.id]["time_slot2"]

        region = (self.time_order[time_slot1], self.time_order[time_slot2])

        return region

    def tier_has_regions(self, tier):
        """This method check if a tier has regions.
        The tiers that are considerate with regions
        are the ones that theirs "LINGUISTIC_TYPE"
        is "TIME_ALIGNABLE" true.

        Parameters
        ----------
        tier : object
            Tier to check if has regions.

        Returns
        -------
        boolean : bool
            Result of the TIME_ALIGNABLE check.

        """

        for l in self.tree.findall("LINGUISTIC_TYPE"):
            if l.attrib["LINGUISTIC_TYPE_ID"] == tier.linguistic_type:
                if l.attrib['TIME_ALIGNABLE'] == 'true':
                    return True

        return False

    def get_primary_data(self):
        """This method gets the information about
        the source data file.

        Returns
        -------
        primary_data : object
            PrimaryData object.

        """

        primary_data = poioapi.io.graf.PrimaryData()

        media_descriptor = None
        media_descriptors = self.tree.find("HEADER").findall(
            "MEDIA_DESCRIPTOR")
        if len(media_descriptors) > 0:
            #TODO: Can exist more than one media_descriptor so we only get the first
            media_descriptor = media_descriptors[0]

            if media_descriptor.attrib["MIME_TYPE"].startswith("video"):
                primary_data.type = poioapi.io.graf.VIDEO
            elif media_descriptor.attrib["MIME_TYPE"].startswith("audio"):
                primary_data.type = poioapi.io.graf.AUDIO

            primary_data.external_link = media_descriptor.attrib["MEDIA_URL"]
        else:
            header = self.tree.find("HEADER")
            if 'MEDIA_FILE' in header.attrib:
                primary_data.type = poioapi.io.graf.UNKNOWN
                primary_data.external_link = header.attrib['MEDIA_FILE']

        return primary_data

    def _map_time_slots(self):
        """This method map "TIME_SLOT_ID"s with
        their respective values.

        Returns
        -------
        time_order_dict : dict
            A dictonary with the time slot's and their values.

        See also
        --------
        _fix_time_slots

        """

        # TODO: For the last time_slot if it's empty should be take from the
        # audio/video file. If there's no audio/video file the value should be
        # -1.

        time_order = self.tree.find('TIME_ORDER')
        time_order_dict = dict()

        for idx, time in enumerate(time_order):
            key = time.attrib['TIME_SLOT_ID']

            if 'TIME_VALUE' in time.attrib:
                value = int(time.attrib['TIME_VALUE'])
            elif idx == len(time_order) - 1:
                value = -1
            else:
                value = None

            time_order_dict[key] = value

        time_order_dict = self._fix_time_slots(time_order_dict)

        return time_order_dict

    def _fix_time_slots(self, time_order_dict):
        """Helper function that fix some of the missing
        values in the time slots. Some of the "TIME_SLOT_ID"
        doesn't contain the "TIME_VALUE" since this
        attribute is optional.

        Parameters
        ----------
        time_order_dict : dict
            A dictonary with the time slot's and their values.

        Returns
        -------
        time_order_dict : dict
            A dictonary with the time slot's and their values.

        See also
        --------
        _find_time_slot_value

        """

        for time_slot, value in time_order_dict.items():
            if value is None:
                time_order_dict[time_slot] = self._find_time_slot_value(
                    time_slot, time_order_dict)

        return time_order_dict

    def _find_time_slot_value(self, time_slot, time_order_dict):
        """Helper function to find and calculate the missing
        time value. The calculation is made base in the range
        where the time slot is used. The First it's obtain the
        range values then is made a summation of that values
        and divide by the number of values. In the end it's
        a mean count.

        Parameters
        ----------
        time_slot : str
            Id of a "TIME_ORDER".
        time_order_dict : dict
            A dictonary with the time slot's and their values.

        Returns
        -------
        time_slot_value : int
            Time value of a specific time slot.

        """

        tiers = self.tree.findall('TIER')
        range_time_slots = []

        for tier in tiers:
            annotations = tier.findall('ANNOTATION')
            for annotation in annotations:
                if annotation[0].tag == 'ALIGNABLE_ANNOTATION':
                    if annotation[0].attrib['TIME_SLOT_REF1'] == time_slot:
                        range_time_slots.append(
                            annotation[0].attrib['TIME_SLOT_REF2'])
                    if annotation[0].attrib['TIME_SLOT_REF2'] == time_slot:
                        range_time_slots.append(
                            annotation[0].attrib['TIME_SLOT_REF1'])

        time_slot_value = 0

        for time_slot in range_time_slots:
            time_slot_value += time_order_dict[time_slot]

        if len(range_time_slots) is not 0:
            time_slot_value = (time_slot_value / len(range_time_slots))

        return time_slot_value

    def _retrieve_aditional_information(self):
        """This method retrieve all the elan
        core file, except the ANNOTATION tags,
        to make it possible to reconstruct the
        elan file again.

        Returns
        -------
        meta_information : ElementTree
            Element with all the elan elements except the Tiers
            annotations.

        """

        meta_information = Element(self.root._root.tag, self.root._root.attrib)

        for element in self.tree:
            if element.tag != 'ANNOTATION_DOCUMENT':
                if element.tag == 'TIER':
                    meta_information.append(Element(
                        element.tag, element.attrib))
                else:
                    parent_element = SubElement(meta_information, element.tag,
                                                element.attrib)
                    for child in element:
                        other_child = SubElement(parent_element, child.tag,
                                                 child.attrib)

                        # Update time_slots
                        if other_child.tag == "TIME_SLOT" and \
                                "TIME_VALUE" not in other_child:
                            other_child.attrib["TIME_VALUE"] = \
                                "{0}".format(self.time_order[
                                    other_child.attrib["TIME_SLOT_ID"]])

                        if not str(child.text).isspace() or \
                                child.text is not None:
                            other_child.text = child.text

        return meta_information


class Writer(poioapi.io.graf.BaseWriter):
    """
    Class that will handle the writing of
    GrAF files into Elan files again.

    """

    def write(self, outputfile, converter): #graf_graph, tier_hierarchies, primary_data=None, meta_information=None):
        """Write the GrAF object into a Elan file.

        Parameters
        ----------
        outputfile : str
            The filename of the output file. The filename should have
            the Elan extension ".eaf".
        graf_graph : obejct
            A GrAF object.
        tier_hierarchies : array_like
            Array with all the tier hierarchies from the GrAF.
        primary_data : object
            This object will contain the information to the dataDesc
            primaryData.
        meta_information : ElementTree
            Element tree contains all the information in Elan file
            besides the Tiers annotations.

        """

        self._time_slot_id = 0
        self.time_order = self._map_time_slots(converter.meta_information)

        for tier in self._flatten_hierarchy_elements(
                converter.tier_hierarchies):
            element = self._tier_in_meta_information(tier,
                converter.meta_information)
            if element is not None:
                for node in converter.graf.nodes:
                    if node.id.startswith("{0}..".format(tier)):
                        for ann in node.annotations:

                            annotation_value, ann_type, features = \
                                self.get_annotation_values(node, ann)

                            annotation_element = SubElement(
                                element, 'ANNOTATION')
                            new_ann = SubElement(
                                annotation_element, ann_type, features)
                            SubElement(
                                new_ann, 'ANNOTATION_VALUE').text = \
                                annotation_value

        self._write_file(outputfile, converter.primary_data,
            converter.meta_information)

    def _tier_in_meta_information(self, tier, meta_information):
        for et in meta_information.findall("TIER"):
            if et.attrib["TIER_ID"] == tier.split(
                    poioapi.io.graf.GRAFSEPARATOR)[1]:
                return et

        return None

    def get_annotation_values(self, node, ann):
        features = {'ANNOTATION_ID': ann.id}
        annotation_value = None

        if node.links:
            ann_type = "ALIGNABLE_ANNOTATION"

            anchors = node.links[0][0].anchors
            features['TIME_SLOT_REF1'] = self._time_order(anchors[0])
            features['TIME_SLOT_REF2'] = self._time_order(anchors[1])
        else:
            ann_type = "REF_ANNOTATION"
            previous_annotation = self._find_previous_annotation(node)

            features["ANNOTATION_REF"] = node.parent.annotations._elements[0].id

            if previous_annotation:
                features["PREVIOUS_ANNOTATION"] = previous_annotation

        if "annotation_value" in ann.features:
            annotation_value = ann.features['annotation_value']

        for key, feature in ann.features.items():
            if key != "annotation_value":
                features[key] = feature

        return annotation_value, ann_type, features

    def _time_order(self, anchor):
        if anchor in self.time_order:
            return self.time_order[anchor]
        else:
            time_slot_id = self._next_time_slot()
            self.time_order[anchor] = time_slot_id
            return time_slot_id

    def _next_time_slot(self):
        self._time_slot_id += 1
        time_slot_id = "ts{0}".format(self._time_slot_id)

        return time_slot_id

    def _find_previous_annotation(self, node):
        parent = node.parent

        prev_node = None
        neighbours = [child for child in parent.iter_children()
                            if child.id.startswith(node.id.rpartition(
                                poioapi.io.graf.GRAFSEPARATOR)[0])]
        for neighbour in neighbours:
            if neighbour.id == node.id:
                break
            prev_node = neighbour
        if prev_node:
            return prev_node.annotations.get_first().id

        return None

    def _write_file(self, outputfile, primary_data, element_tree):
        """Write and indent the element tree into a
        Elan file.

        Parameters
        ----------
        outputfile : str
            The filename of the output file. The filename should have
            the Elan extension ".eaf".
        element_tree : ElementTree
            Element tree with all the information.

        """

        file = open(outputfile, 'wb')
        time = element_tree.find("TIME_ORDER")
        for t in time:
            if t.attrib["TIME_VALUE"] == "-1":
                del t.attrib["TIME_VALUE"]
                
        if primary_data:
            if primary_data.type != "none" and not element_tree.find("HEADER"):
                header = SubElement(element_tree, "HEADER",
                                    {"MEDIA_FILE": " ",
                                    "TIME_UNITS": "milliseconds"})
                SubElement(header, "MEDIA_DESCRIPTOR",
                           {"MEDIA_URL": primary_data.external_link,
                            "MIME_TYPE": primary_data.type})

        doc = minidom.parseString(tostring(element_tree))
        file.write(doc.toprettyxml(indent='    ', encoding='UTF-8'))
        file.close()

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

    def _map_time_slots(self, meta_information):
        """This method map "TIME_SLOT_ID"s with
        their respective values.

        Parameters
        ----------
        meta_information : ElementTree
            Element tree contains the information about the
            TIME_ORDER.

        Returns
        -------
        time_order : dict
            A dictonary with the time slot's and their values.

        """

        time_order = {}

        for time in meta_information.find('TIME_ORDER'):
            time_order[time.attrib['TIME_VALUE']] = time.attrib['TIME_SLOT_ID']

        return time_order

