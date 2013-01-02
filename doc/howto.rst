*******************
How To Use Poio API
*******************

This is the documentation for Python Libary Poio API.

Introduction
============  

This document has as presupposition explation the some functions of the Poio API Library. Those functions are how to parse the GrAF files to Annotation Tree and how to transform an Annotation Tree to the GrAF files.

First is important to know how the process of each function works.
The transformation if an Annotation Tree to the GrAF files is made by giving an Annotation Tree that contains a specific data structure hierarchy and then the necessary files using the GrAF ISO standards, are generated. Each of the files created are followed by the extension that corresponds to each element in the data structure hierarchy (e.g. 'filename-utterance.xml'). In the end a header file is created.
This header file in the GrAF ISO standard is the file that contain the relevant information about the GrAF. The information passes by the author, date of creation... The most important part of the files are the annotations and the primary file. The annotations are the dependent files to create all the nodes, edges, feature and everything needed to the GrAF. The primary file is the raw file that has the words that are the values of the nodes.
To parse the Graf to Annotation Tree files will be necessary an header file and give the respective data structure hiearchy.

Next is shown the two processes.

Before we get to the example is important to be familiar with the data structure used in Poio API.

The data structure used in this example is based in GRAID annotations (For more detailed information http://www.linguistik.uni-kiel.de/GRAID_manual6.0_08sept.pdf)

Data Structure [GRAID Structure]

.. code-block:: python

	[ 'utterance',
		[ 'clause unit',
			[ 'word', 'wfw', 'graid1' ],
		'graid2' ],
	  'translation', 'comment' ]

NOTE: The explanations in this document focus only on the graf.py of the Poio API Library.

Annotation Tree to GrAF
=======================

The descriptions below can be used with the script in the examples folder called pickle2graf.py.

The first step is to initialize the variable:

.. code-block:: python

	data_hierarchy = data.DataStructureTypeGraid()
	annotation_tree = annotationtree.AnnotationTree(data_hierarchy)

The Annotation Tree will contain the hierarchy and relations between the elements between which sentence, word, wfw and it's translation.
In this step what is done is to set the data structure type of the tree with **Annotation Tree(data.DataStructureTypeGraid)**.

The second step is to load the Annotation Tree (in the example_data folder there are some example files):

.. code-block:: python

	annotation_tree.load_tree_from_pickle(inputfile)

At this point is important to know that the file should be a **pickle** file and must be previously created with PoioUI (https://github.com/cidles/Poio).

The third and last step is call the writer of the GrAF:

.. code-block:: python

	writer = Writer(annotation_tree, output)
	writer.write()

NOTE: The generated files are in the same folder as the inputfile.

Parse GrAF files to Annotation Tree
===================================
		
Is important to know that to make the parsing of the GrAF files they must be createad as well as the header file.
The parsing of the files using Poio API module allows to reverse from GrAF to the Annotation Tree.


The first step is to initialize the variable. Once again is need to give the correct data structure hierarchy that was given to create the header file (or transform the Annotation Tree into GrAF ISO in this case):

.. code-block:: python

	data_hierarchy = data.DataStructureTypeGraid()

The second is to initialize the Annotation Tree and the Parser itself:

.. code-block:: python

	annotation_tree = annotationtree.AnnotationTree(data_hierarchy)
	parser = graf.Parser(annotation_tree, headerfile)

And then is possible to create the Annotation Tree again:

.. code-block:: python

	annotation_tree = parser.load_as_tree()
	
	# Consulting the elements
	for element in annotation_tree.elements():
		print(element)

Resources
=========
Source File :download:`pickle2graf.py<_resources/pickle2graf.py>`.