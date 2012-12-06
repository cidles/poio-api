# -*- coding: utf-8 -*-
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
"""This module contains classes to access Elan data.

The class Eaf is a low level API to .eaf files.

EafGlossTree, EafPosTree, etc. are the classes to access the data via
tree, which also contains the original .eaf IDs. Because of this
EafTrees are read-/writeable.
"""

from poioapi.io.analyzer import XmlContentHandler

file = '/home/alopes/tests/elan/example.eaf'
content = XmlContentHandler(file)
content.parse()

data_structure_hierarchy = []
for value in content.elan_map:
    if value[0] == 'TIER':
        for element in value[1]:
            if 'TIER_ID' in element:
                result = element.split('TIER_ID - ')
                data_structure_hierarchy.append(result[1])

print(data_structure_hierarchy)
