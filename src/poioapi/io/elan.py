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

from __future__ import absolute_import, unicode_literals

import xml.etree.ElementTree as ET

from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

import poioapi.io.graf

class ElanTier(poioapi.io.graf.Tier):
    __slots__ = ["linguistic_type"]

    def __init__(self, name, linguistic_type):
        self.linguistic_type = linguistic_type

        try:
            self.annotation_space = self.linguistic_type.encode("utf-8").replace(' ', '_')
        except :
            self.annotation_space = self.linguistic_type.replace(' ', '_')

        self.name = self.annotation_space + "/" + name


class Parser(poioapi.io.graf.BaseParser):
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

        self.filepath = filepath

        self.parse()

    def parse(self):
        """This method will set the variables
        to make possible to do the parsing
        correctly.

        """

        self.root = ET.parse(self.filepath)
        self.tree = self.root.getroot()
        self.regions_map = self._map_time_slots()
        self.meta_information = self._retrieve_aditional_information()

    def get_root_tiers(self):
        """This method retrieves all the root tiers.
        In this case the root tiers are all those
        that doesn't contain "PARENT_REF".

        Returns
        -------
        list : array-like
            List of tiers type.

        """

        return [ElanTier(tier.attrib['TIER_ID'], tier.attrib['LINGUISTIC_TYPE_REF'])
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

        child_tiers = []

        tier_name = tier.name.split("/")[1]

        for t in self.tree.findall("TIER"):
            if "PARENT_REF" in t.attrib and t.attrib["PARENT_REF"] == tier_name:
                child_tiers.append(ElanTier(t.attrib['TIER_ID'],
                    t.attrib['LINGUISTIC_TYPE_REF']))

        return child_tiers

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

        annotations = []
        tier_annotations = []

        tier_name = tier.name.split("/")[1]

        for t in self.tree.findall("TIER"):
            if t.attrib["TIER_ID"] == tier_name:
                if annotation_parent is not None and self.tier_has_regions(tier) == False:
                    for a in t.findall("ANNOTATION/*"):
                        if a.attrib["ANNOTATION_REF"] == annotation_parent.id:
                            tier_annotations.append(a)
                    break
                else:
                    tier_annotations = t.findall("ANNOTATION/*")
                    break

        for annotation in tier_annotations:
            annotation_id = annotation.attrib['ANNOTATION_ID']
            annotation_value = annotation.find('ANNOTATION_VALUE').text

            if annotation.tag == "ALIGNABLE_ANNOTATION":
                if annotation_parent is None:
                    features = {'time_slot1':annotation.attrib['TIME_SLOT_REF1'],
                                'time_slot2':annotation.attrib['TIME_SLOT_REF2']}
                elif self._find_ranges_in_annotation_parent(annotation_parent, annotation):
                    features = {'time_slot1':annotation.attrib['TIME_SLOT_REF1'],
                                'time_slot2':annotation.attrib['TIME_SLOT_REF2']}
                else:
                    continue
            else:
                annotation_ref = annotation.attrib['ANNOTATION_REF']


                features = {'ref_annotation':annotation_ref,
                            'tier_id':tier_name}

                for attribute in annotation.attrib:
                    if attribute != 'ANNOTATION_REF' and attribute != 'ANNOTATION_ID' and\
                       attribute != 'ANNOTATION_VALUE':
                        features[attribute] = annotation.attrib[attribute]

            annotations.append(poioapi.io.graf.Annotation(annotation_id, annotation_value, features))

        return annotations

    def _find_ranges_in_annotation_parent(self, annotation_parent, annotation):

        if annotation_parent is not None:
            annotation_parent_regions = self.region_for_annotation(annotation_parent)

            annotation_regions = [int(self.regions_map[annotation.attrib['TIME_SLOT_REF1']]),
                                  int(self.regions_map[annotation.attrib['TIME_SLOT_REF2']])]

            if annotation_parent_regions[0] <= annotation_regions[0]\
            and annotation_regions[1] <= annotation_parent_regions[1] :
                return True

        return False

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

        if 'time_slot1' in annotation.features:
            part_1 = int(self.regions_map[annotation.features['time_slot1']])
            part_2 = int(self.regions_map[annotation.features['time_slot2']])

            region = (part_1, part_2)

            return region

        return None

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

        time_order = self.tree.find('TIME_ORDER')
        time_order_dict = dict()

        for time in time_order:
            key = time.attrib['TIME_SLOT_ID']

            if 'TIME_VALUE' in time.attrib:
                value = time.attrib['TIME_VALUE']
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
                time_order_dict[time_slot] = self._find_time_slot_value(time_slot,
                    time_order_dict)

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
                        range_time_slots.append(annotation[0].attrib['TIME_SLOT_REF2'])
                    if annotation[0].attrib['TIME_SLOT_REF2'] == time_slot:
                        range_time_slots.append(annotation[0].attrib['TIME_SLOT_REF1'])

        time_slot_value = 0

        for time_slot in range_time_slots:
            time_slot_value += int(time_order_dict[time_slot])

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
            Element with all the elan elements.

        """

        meta_information = Element(self.root._root.tag,
            self.root._root.attrib)

        for element in self.tree:
            if element.tag == 'TIER':
                meta_information.append(Element(element.tag,element.attrib))
            else:
                meta_information.append(element)

        return meta_information


class Writer:
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

    def write(self):
        """This method will look into the metafile
        and then reconstruct the Elan file.

        """

        tree = ET.parse(self.extinfofile).getroot()

        miscellaneous = tree.findall('./miscellaneous/')
        element_tree = Element(miscellaneous[0].tag, miscellaneous[0].attrib)

        for element in miscellaneous:
            if element.tag != 'ANNOTATION_DOCUMENT':
                parent_element = SubElement(element_tree, element.tag,
                    element.attrib)
                for child in element:
                    other_chid = SubElement(parent_element, child.tag,
                        child.attrib)
                    if not str(child.text).isspace() or\
                       child.text is not None:
                        other_chid.text = child.text

        namespace = "{http://www.w3.org/XML/1998/namespace}"

        for tiers in tree.findall('./header/tier_mapping/'):
            linguistic_type = tiers.attrib['name'].replace(' ','_')

            for tiers_id in tiers:
                tier_id = tiers_id.text

                graf_tree = ET.parse(self.extinfofile.replace("-extinfo",
                    "-"+linguistic_type)).getroot()

                annotations = graf_tree.findall('{http://www.xces.org/ns/GrAF/1.0/}a')

                tier_element_tree = element_tree.find("TIER[@TIER_ID='"+tier_id+"']")

                linguistic_type_ref = element_tree.find("LINGUISTIC_TYPE[@LINGUISTIC_TYPE_ID='"+
                                                        tier_element_tree.attrib['LINGUISTIC_TYPE_REF']+"']")

                for annotation in annotations:
                    features_map = {}
                    feature_structure = annotation[0]

                    if tier_id+"/" in annotation.attrib['ref']:
                        if linguistic_type_ref.attrib['TIME_ALIGNABLE'] == 'true':
                            features_map['ANNOTATION_ID'] = annotation.attrib[namespace+"id"]
                            features_map['TIME_SLOT_REF1'] = feature_structure[0].text
                            features_map['TIME_SLOT_REF2'] = feature_structure[1].text

                            annotation_element = SubElement(tier_element_tree,
                                'ANNOTATION')
                            alignable_annotation = SubElement(annotation_element,
                                'ALIGNABLE_ANNOTATION',features_map)
                            SubElement(alignable_annotation,
                                'ANNOTATION_VALUE').text = self._get_annotation_value(feature_structure)
                        else:
                            features_map['ANNOTATION_ID'] = annotation.attrib[namespace+"id"]
                            features_map['ANNOTATION_REF'] = feature_structure[0].text

                            for feature_element in feature_structure:
                                if feature_element.attrib['name'] != 'ref_annotation' and\
                                   feature_element.attrib['name'] != 'annotation_value' and\
                                   feature_element.attrib['name'] != 'tier_id':
                                    key = feature_element.attrib['name']
                                    features_map[key] = feature_element.text

                            annotation = SubElement(tier_element_tree, 'ANNOTATION')
                            ref_annotation = SubElement(annotation,
                                'REF_ANNOTATION',features_map)
                            SubElement(ref_annotation, 'ANNOTATION_VALUE').text =\
                            self._get_annotation_value(feature_structure)

        file = open(self.outputfile,'wb')
        doc = minidom.parseString(tostring(element_tree))
        file.write(doc.toprettyxml(indent='    ', encoding='UTF-8'))
        file.close()

    def _get_annotation_value(self, feature_structure):
        try:
            annotation_value = feature_structure[2].text
        except:
            annotation_value = None

        return annotation_value