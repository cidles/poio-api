import ann_tree_rec
import txtrawfile
import segclauseunit
import segfilewords
import segfilewfw
import segfilegraid1
import segfilegraid2
import segfiletrans
import segfilecomment
import xmltograf

filepath = '/home/alopes/tests/pi_2.pickle'

# AnnotationTree (pickle) to GrAF annotations
raw = txtrawfile.CreateRawFile(filepath)
raw.create_raw_file()

clause_unit = segclauseunit.CreateSegClauseUnits(filepath)
clause_unit.create_clause_units_file()

words = segfilewords.CreateSegWords(filepath)
words.create_words_file()

wfws = segfilewfw.CreateWfwFile(filepath)
wfws.create_wfw_xml()

graid1 = segfilegraid1.Creategraid1File(filepath)
graid1.create_graid1_xml()

graid2 = segfilegraid2.Creategraid2File(filepath)
graid2.create_graid2_xml()

translation = segfiletrans.CreateTransFile(filepath)
translation.create_trans_xml()

comment = segfilecomment.CreateCommentFile(filepath)
comment.create_cmts_xml()

# XML (in GrAF) to AnnotationTree (pickle)
ann_tree_rec.main(filepath)

# AnnotationTree (XML) to GrAF
graf = xmltograf.RendToGrAF(filepath)
graf.parse_xml_graf('wfw')