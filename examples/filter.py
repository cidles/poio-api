# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: Peter Bouda <pbouda@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

import codecs
import poioapi.annotationgraph

# Load an annotation graph from example file at:
# http://tla.mpi.nl/tools/tla-tools/elan/download
ag = poioapi.annotationgraph.AnnotationGraph()
ag.from_elan("elan-example3.eaf")

# Set one of the tier hierarchies as our "working" hierarchy
tier_hierarchy = None
for t in ag.tier_hierarchies:
    if t[0] == "utterance..W-Spch":
        tier_hierarchy = t
ag.structure_type_handler = poioapi.data.DataStructureType(
    tier_hierarchy)

# Create filter manually
af = poioapi.annotationgraph.AnnotationGraphFilter(ag)
af.set_filter_for_tier("words..W-Words", "follow")
af.set_filter_for_tier("part_of_speech..W-POS", r"\bpro\b")

ag.append_filter(af)

print("Filtered root nodes:")
print(ag.filtered_node_ids)

# Remove filter again
ag.pop_filter()

# Create filter from dict
search_terms = {
    "words..W-Words": "follow",
    "part_of_speech..W-POS": r"\bpro\b"
}
af = ag.create_filter_for_dict(search_terms)

ag.append_filter(af)

print("Filtered root nodes:")
print(ag.filtered_node_ids)

# write result as HTML
html = ag.as_html_table(True)
f = codecs.open("test.html", "w", "utf-8")
f.write(html)
f.close()

