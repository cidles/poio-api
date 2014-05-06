# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2014 Poio Project
# Author: Peter Bouda <pbouda@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

from __future__ import unicode_literals

import poioapi.data
import os.path
import json
import sys


def list_from_json_dict(json_dict):
    """ This function converts a dictionary to a list by transforming each key/value pair of the dictionary
        into a tuple. This tuple is in the format: (dictionary_key, dictionary_value). If one of the dictionary
        keys has multiple tags, then we split them and create a tuple with the result.

        Parameters
        ----------
        json_dict : dictionary
        This is one of the dictionaries loaded from a JSON file containing the mapping rules.

         Return
         ------
         mapping : list
         A list containing the tuples created from the json_dict's key/value pairs
    """
    mapping = []
    for key in json_dict.keys():
        extra_mapping_key = key
        split = key.split(', ')

        if len(split) > 1:
            extra_mapping_key = tuple(split)
        if isinstance(json_dict[key], list):
            mapping.append((extra_mapping_key, tuple(json_dict[key])))
        else:
            mapping.append((extra_mapping_key, json_dict[key]))

    return mapping

tag_separators = '[\.,]'

class MalformedJsonFile(Exception):
    pass


class TierMapper(object):

    _tier_mapping_name = 'tier_names'
    _tier_mapping = {}

    def __init__(self):
        pass

    def load_mapping(self, file_path):
        """ This method initializes the tier and tag mappings.
            It also validates the structure of the JSON file supplied

            Parameters
            ----------
            file_path : str
                The path of the JSON file to be read.

        """

        #if the file_path is None or empty do nothing.
        #if the file does not exist, the method returns an error.
        if file_path is not None and file_path != '':
            if os.path.exists(file_path):
                #load the entire object
                json_file = open(file_path, 'r')
                mappings = json.load(json_file)
                json_file.close()

                #load the mapping of the tier names for each type
                if self._tier_mapping_name in mappings.keys():
                    self._tier_mapping = dict()
                    mapping = mappings[self._tier_mapping_name]
                    if isinstance(mapping, dict):
            #this cycle is to ignore any tier mapping whose key is not defined in the tier_labels dictionary
                        for key in poioapi.data.tier_labels.keys():
                            try:
                                if isinstance(mapping[poioapi.data.tier_labels[key]], list):
                                    self.append_to_tier_labels(key, mapping[poioapi.data.tier_labels[key]])
                                else:
                                    raise MalformedJsonFile('The tier mapping should be a list')
                            except KeyError:
                                pass

            else:
                raise IOError('File was not found')

    def tier_label(self, tier_identifier, label_index=0):
        """ This function return a specific label from the tag mapping.

            Parameters
            ----------
            tier_identifier : int
                The tier from which to extract the tag. Must be one of the keys of tier_labels
            label_index : int
                The label index inside the list of labels for the desired tier. If this parameter is ommited,
                the returned label is the first in the list

            Return
            ------
            label : str
                The desired label
        """
        if tier_identifier is None or not isinstance(tier_identifier, int):
            raise ValueError('The tier_identifier must be an integer.')

        if tier_identifier not in self._tier_mapping.keys():
            raise ValueError('The specified tier does not exist.')

        label = self._tier_mapping[tier_identifier][label_index]
        return label

    def tier_labels(self, tier_identifier):
        """ Function to return all the mapped labels for a given tier.

            Parameter
            ---------
            tier_identifiers : int
                The tier from which to extract the tag. Must be one of the keys of tier_labels

            Return
            ------
            labels : list
                The labels mapped to the specified tier
        """
        if tier_identifier is None or not isinstance(tier_identifier, int):
            raise ValueError('The tier_identifier must be an integer.')

        labels = []
        if tier_identifier in self._tier_mapping.keys():
            labels = self._tier_mapping[tier_identifier]

        return labels

    def append_to_tier_labels(self, tier_identifier, new_value):
        if tier_identifier is None or not isinstance(tier_identifier, int):
            raise ValueError('The tier_identifier parameter must be an integer.')
        if not isinstance(new_value, list):
            raise ValueError('The new_value parameter must be a list')

        if tier_identifier not in self._tier_mapping.keys() or self._tier_mapping[tier_identifier] is None:
            self._tier_mapping[tier_identifier] = []

        for val in new_value:
            if val not in self._tier_mapping[tier_identifier]:
                self._tier_mapping[tier_identifier].append(val)


class AnnotationMapper(object):

    def __init__(self, source_type, destination_type):
        self._annotation_mappings = dict()
        self.missing_tags = dict()
        file_name = '{0}_{1}.json'.format(poioapi.data.type_names[source_type],
                                          poioapi.data.type_names
                                          [destination_type])

        file_name = os.path.join(os.path.dirname(__file__), "mappings",
                                 file_name)

        self.load_mappings(file_name)

    def annotation_mappings():
        doc = "The annotation_mappings property."

        def fget(self):
            return self._annotation_mappings

        def fset(self, value):
            if os.path.exists(value):
                self.load_mappings(value)
            else:
                raise ValueError('The specified file does not exist.')

        def fdel(self):
            del self._annotation_mappings
        return locals()
    annotation_mappings = property(**annotation_mappings())

    def load_mappings(self, file_path):
        """ This function loads the mappings defined in the file passed as
        parameter.

            Parameter
            ---------
            file_path : str
                The path of the file that contains the mapping.
        """
        if file_path is not None and file_path != '':
            if os.path.exists(file_path):
                #load the entire object
                json_file = open(file_path, 'r')
                mappings = json.load(json_file)
                json_file.close()

                for key in poioapi.data.tier_labels.keys():
                    if poioapi.data.tier_labels[key] in mappings.keys():
                        for k, v in list_from_json_dict(mappings[poioapi.data.
                                tier_labels[key]]):
                            if key in self._annotation_mappings.keys():
                                if k not in [k1 for k1, v1 in
                                             self._annotation_mappings[key]]:
                                    self._annotation_mappings[key].append((k,
                                                                           v))
                            else:
                                self._annotation_mappings[key] = []
                                self._annotation_mappings[key].append((k, v))
            else:
                raise IOError('File was not found')

    def validate_tag(self, tier_label, tag_to_validate):
        """ This function validates if a tag is present in the specified tier
            tag mapping.

            Parameters
            ----------
            tier_to_validate : str
                The tier label as defined in the tier mapping
            tag_to_validate : str
                The value for which to perform the check.

            Return
            ------
            value : str or list
                The corresponding tag mapping for tag_to_validate if it is
                present. Else returns 'None'. If the mapping is for other tier
                the return wil be a list
        """
        #some validations on incorrect parameter definition
        if tier_label is None or tier_label == '':
            raise ValueError('Incorrect tier label')

        if tag_to_validate is not None or tag_to_validate != '':

            #if the tag is already missing there is no point in re-checking
            if tier_label in self.missing_tags.keys() and tag_to_validate in \
                    self.missing_tags[tier_label].keys():
                return None

            #perform the validation
            value = None
            if tier_label in self._annotation_mappings.keys() and \
                            self._annotation_mappings[tier_label] is not None:
                for key, val in self._annotation_mappings[tier_label]:
                    #handling the N-1 tag correspondence
                    if isinstance(key, tuple):
                        if tag_to_validate.upper() in key:
                            value = val
                            break
                    else:
                        if tag_to_validate.upper() == key.upper():
                            value = val
                            break

        return value

    def add_to_missing(self, tier_label, tag):
        """ This method adds a tag to the missing dictionary for the
            corresponding tier_label.

            Parameters
            ----------
            tier_label : str
                The tier name to which the tag is to be added.
            tag : str
                The tag value that is missing.
        """

        if tier_label is None or tier_label == '' or tier_label not \
                in poioapi.data.tier_labels.keys():
            raise ValueError('Incorrect tier label')

        if tag is not None and tag != '':
            if tier_label not in self.missing_tags.keys():
                self.missing_tags[tier_label] = {}
            self.missing_tags[tier_label][tag] = ''
        else:
            raise ValueError(
                'The tag parameter must not be None or an empty string')

    def export_missing_tags(self, output_file):
        """ This method exports the tier mapping and the missing tags
            dictionaries to a JSON file. After filling in the result file, the
            user should use it as the parameter for the instantiation of this
            class.

            Parameters
            ----------
            output_file : str
                The path of the file that will be the result of the export.
        """
        #building the output dictionary
        output = dict()

        for key in self.missing_tags.keys():
            output[poioapi.data.tier_labels[key]] = self.missing_tags[key]

        #export the JSON file
        file = open(output_file, 'w')
        json.dump(output, file, ensure_ascii=False, indent=4, separators=(',', ': '), sort_keys=True)
        file.close()