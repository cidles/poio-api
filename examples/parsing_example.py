# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
"""This module contains a simple example 
how to use the PoioAPI Parser.
"""

from poioapi.parser import xmltoanntree
from poioapi.parser import xmltograf
from poioapi.parser import txtrawfile
from poioapi.parser import translation
from poioapi.parser import comment
from poioapi.parser import graid_clauseunit
from poioapi.parser import graid_words
from poioapi.parser import graid_wfw
from poioapi.parser import graid_graid1
from poioapi.parser import graid_graid2
from poioapi.parser import morph_gloss
from poioapi.parser import morph_morphemes
from poioapi.parser import morph_words
from poioapi.parser import header

filepath = 'Balochi Text1.pickle'

header = header.CreateHeaderFile(filepath)
header.author = 'Author'

# AnnotationTree (pickle) to GrAF annotations
txt =  txtrawfile.CreateRawFile(filepath)
txt.create_raw_file()
header.filename = txt.filename
header.primaryfile = txt.file

trs = translation.CreateTransFile(filepath)
trs.create_trans_xml()
header.add_annotation(trs.loc, trs.fid)

cmt = comment.CreateCommentFile(filepath)
cmt.create_cmts_xml()
header.add_annotation(cmt.loc, cmt.fid)

# GRAID data hierarchy
clause = graid_clauseunit.CreateClauseUnitsFile(filepath)
clause.create_clause_units_file()
header.add_annotation(clause.loc, clause.fid)

words = graid_words.CreateGraidWordsFile(filepath)
words.create_words_file()
header.add_annotation(words.loc, words.fid)
header.unitcount = words.wordcount

wfw = graid_wfw.CreateWfwFile(filepath)
wfw.create_wfw_xml()
header.add_annotation(wfw.loc, wfw.fid)

graid1 = graid_graid1.CreateGraid1File(filepath)
graid1.create_graid1_xml()
header.add_annotation(graid1.loc, graid1.fid)

graid2 = graid_graid2.CreateGraid2File(filepath)
graid2.create_graid2_xml()
header.add_annotation(graid2.loc, graid2.fid)

# Morphemsyntax data hierarchy
morphw = morph_words.CreateMorphWordsFile(filepath)
morphw.create_words_file()
header.add_annotation(morphw.loc, morphw.fid)

morphemes = morph_morphemes.CreateMorphemesFile(filepath)
morphemes.create_morphs_file()
header.add_annotation(morphemes.loc, morphemes.fid)

gloss = morph_gloss.CreateMorphGlossFile(filepath)
gloss.create_gloss_xml()
header.add_annotation(gloss.loc, gloss.fid)

header.create_header()

# XML (in GrAF) to AnnotationTree (pickle)
xmltoanntree.XmlToAnnTree().graid_hierarchy(filepath) # GRAID
xmltoanntree.XmlToAnnTree().morph_hierarchy(filepath) # Morphemes
xmltoanntree.XmlToAnnTree().word_hierarchy(filepath) # Words

# AnnotationTree (XML) to GrAF
graf = xmltograf.RendToGrAF(filepath)

# Choose a type of GrAF Graid1/2, WfW or Gloss
graf.parse_xml_graf('wfw')
#graf.parse_xml_graf('graid1')
#graf.parse_xml_graf('word')
