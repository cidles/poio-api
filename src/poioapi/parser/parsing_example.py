import xmltoanntree
import xmltograf
import txtrawfile
import translation
import comment
import graid_clauseunit
import graid_words
import graid_wfw
import graid_graid1
import graid_graid2
import morph_gloss
import morph_morphemes
import morph_words

filepath = '/home/alopes/tests/pi_2.pickle'

# AnnotationTree (pickle) to GrAF annotations
txtrawfile.CreateRawFile(filepath).create_raw_file()

translation.CreateTransFile(filepath).create_trans_xml()

comment.CreateCommentFile(filepath).create_cmts_xml()

# GRAID data hierarchy
graid_clauseunit.CreateClauseUnitsFile(filepath).create_clause_units_file()

graid_words.CreateGraidWordsFile(filepath).create_words_file()

graid_wfw.CreateWfwFile(filepath).create_wfw_xml()

graid_graid1.CreateGraid1File(filepath).create_graid1_xml()

graid_graid2.CreateGraid2File(filepath).create_graid2_xml()

# Morphemsyntax data hierarchy
morph_words.CreateMorphWordsFile(filepath).create_words_file()

morph_morphemes.CreateMorphemesFile(filepath).create_morphs_file()

morph_gloss.CreateMorphGlossFile(filepath).create_gloss_xml()

# XML (in GrAF) to AnnotationTree (pickle)
xmltoanntree.XmlToAnnTree().graid_hierarchy(filepath) # GRAID
xmltoanntree.XmlToAnnTree().morph_hierarchy(filepath) # Morphemes
xmltoanntree.XmlToAnnTree().word_hierarchy(filepath) # Words

# AnnotationTree (XML) to GrAF
graf = xmltograf.RendToGrAF(filepath)

# Choose a type of GrAF Graid1/2, WfW or Gloss
graf.parse_xml_graf('wfw')
graf.parse_xml_graf('graid1')
graf.parse_xml_graf('word')