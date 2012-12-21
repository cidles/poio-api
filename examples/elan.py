import poioapi.io.elan

file = '/home/alopes/tests/elan/example.eaf'
elan_graf = poioapi.io.elan.ElanToGraf(file)

graph = elan_graf.elan_to_graf()

# Just to see the result faster
outputfile = '/home/alopes/tests/elan/example_render.xml'
elan_graf.graf_render(outputfile, graph)