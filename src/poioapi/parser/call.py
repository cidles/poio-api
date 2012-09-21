import ann_tree_rec
import txtrawfile
import segclauseunit
import segfilewords
import segfilewfw

filepath = '/home/alopes/tests/pi_2.pickle'

raw = txtrawfile.CreateRawFile(filepath)
raw.create_raw_file()

words = segfilewords.CreateSegWords(filepath)
words.create_words_file()

wfws = segfilewfw.CreateSegWFW(filepath)
wfws.create_wfw_file()

clause_unit = segclauseunit.CreateSegClauseUnits(filepath)
clause_unit.create_clause_units_file()

ann_tree_rec.main()