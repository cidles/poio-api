from poioapi import data, annotationtree
from poioapi.io.graf import Writer, Parser

filepath = '/home/alopes/tests/pi.pickle'

# Create the data structure
data_hierarchy = data.DataStructureTypeGraid()

# Create the annotation tree with the created data structure
annotation_tree = annotationtree.AnnotationTree(data_hierarchy)

# Open the file
annotation_tree.load_tree_from_pickle(filepath)

search_tier = 'utterance'
update_tiers = ['clause unit', 'word']

# There are problems with the pickle file because of it's encode. Must need to be verified
#annotation_tree.update_elements_with_ranges(search_tier, update_tiers)
#annotation_tree.save_tree_as_pickle('/home/alopes/tests/balochi.pickle')

writ = Writer(annotation_tree, filepath)
writ.write()

#------------------------- PARSER -----------------------------------
#The file should be generated first with the parser
headerfile = '/home/alopes/tests/pi.hdr'

#Parser(headerfile).generate_file()
annotation_tree = annotationtree.AnnotationTree(data_hierarchy)
annotation_tree = Parser(annotation_tree, headerfile).load_as_tree()

for element in annotation_tree.elements():
    print(element)