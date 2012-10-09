# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
"""This module contains a simple example 
how to use the PoioAPI Parser Search in 
GrAF.
"""

from poioapi.parser import search_replace

filepath = 'Balochi Text1-rend.xml'

search_replace = search_replace.SearchReplace(filepath)

# Replace the exact word in the node 339 SUB by SUBS
search_replace.replace_word('SUBS','SUB','wfw-n339')

# Replace all the exact words SUB by SUBS
search_replace.replace_all('SUB','SUBS')

# Find the word SUB
search_res = search_replace.find_word('SUB', False, True)

for search in search_res:
    print(search[0]+' - '+search[1])
