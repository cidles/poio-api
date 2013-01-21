*******************
How To Use Poio API
*******************

This is the documentation for Python Library Poio API.

============
Introduction
============

This document has as presupposition explanation the some functions of the Poio API Library. Those functions are mainly
the parsing of different file formats in to GrAF standardization and vice-versa.

Poio API provides access to language documentation data and a wide range of annotations types stored in different file
formats. It's based on a common and standardized representation format (LAF). The data and annotations can then be used
with existing NLP tools and workflows and hence be combined with any other data source that is isomorphic to the
representations in this framework.

**Note:** The explanations in this document focus only on the module graf.py of the Poio API Library.

====================
Data Structure Types
====================

We use a data type called data structure type to represent the schema of annotation in a tree. A simple data structure
type describing that the researcher wants to tokenize a text into words before adding a word-for-word translation and a
translation for the whole utterance looks like this:

.. code-block:: python

	[ 'utterance', [ 'word', 'wfw' ], 'translation' ]

A slightly more complex annotation schema is GRAID (Grammatical Relations and Animacy in Discourse), developed by
Geoffrey Haig and Stefan Schnell. GRAID adds the notion of clause units as an intermediate layer between utterance and
word and three more annotation tiers on different levels:

.. code-block:: python

	[ 'utterance',
		[ 'clause unit',
			[ 'word', 'wfw', 'graid1' ],
		'graid2' ],
	  'translation', 'comment' ]

One advantage in representing annotation schemes through those simple trees, is that the linguists instantly understand
how such a tree works and can give a representation of "their" annotation schema. In language documentation and general
linguistics researchers tend to create ad-hoc annotation schemes fitting their background and then normally start to
create only those annotations related to their current research project. This is for example reflected in an annotation
software like ELAN, where the user can freely create tiers with any names and arrange them in custom hierarchies. As we
need to map those data into our internal representation, we try to ease the creation of custom annotation schemes that
are easy to understand for users. For this we will allow users to create their own data structure types and derive the
annotation schemes for GrAF files from those structures.

==============
Handling files
==============

To transform any kind of file to GrAF ISO standards using Poio API is necessary to specify data structure hierarchy.
Each of the files created are followed by the extension that corresponds to each element in the data structure hierarchy
(e.g. 'filename-utterance.xml'). A header file is also created.
This header file in the GrAF ISO standard is the file that contain the relevant information about the GrAF. The
information passes by the author, date of creation... The most important part of the that file are the annotations and
the primary file. The annotations represents the dependent files to create all the nodes, edges, feature and everything
else needed to the GrAF. The primary file is the file that contains the raw corpus/information which will be the values
of the nodes.

**Important references**
  * GrAF ISO standards (http://www.iso.org/iso/catalogue_detail.htm?csnumber=37326)

------
Pickle
------

The transformation of an Annotation Tree to the GrAF files is made by giving an Annotation Tree that contains a specific
data structure hierarchy and then the necessary files using the GrAF ISO standards, are generated.

The descriptions below can be used with the script in the examples folder called pickle2graf.py. This example is going
to use mainly the GRAID Annotation structure (http://www.linguistik.uni-kiel.de/GRAID_manual6.0_08sept.pdf).

More information about :doc:`Annotation Tree</annotationtree>`.

^^^^^^^^^^^^^^^^^^^^^^^
Annotation Tree to GrAF
^^^^^^^^^^^^^^^^^^^^^^^

The first step is to initialize the variable:

.. code-block:: python

	data_hierarchy = data.DataStructureTypeGraid()
	annotation_tree = annotationtree.AnnotationTree(data_hierarchy)

The Annotation Tree will contain the hierarchy and relations between the elements between which sentence, word, wfw
and it's translation.
In this step what is done is to set the data structure type of the tree with
**Annotation Tree(data.DataStructureTypeGraid)**.

The second step is to load the Annotation Tree (in the example_data folder there are some example files):

.. code-block:: python

	annotation_tree.load_tree_from_pickle(inputfile)

At this point is important to know that the file should be a **pickle** file and must be previously created with PoioUI
(https://github.com/cidles/Poio).

The third and last step is call the writer of the GrAF:

.. code-block:: python

	writer = Writer(annotation_tree, output)
	writer.write()

NOTE: The generated files are in the same folder as the inputfile.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Parse GrAF files to Annotation Tree
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
		
Is important to know that to make the parsing of the GrAF files they must be created as well as the header file.
The parsing of the files using Poio API module allows to reverse from GrAF to the Annotation Tree.

The first step is to initialize the variable. Once again is need to give the correct data structure hierarchy that
was given to create the header file (or transform the Annotation Tree into GrAF ISO in this case):

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


----
Elan
----

In order to convert the Elan files into GrAF object or GrAF files there is going to be necessary to understand the use
of the data structures hierarchy and the metafile. The data structure describes the relations between tiers. We map each
entry in the data structure to one or more tiers in the elan file.
The data structure elements are going to have the same names as the "LINGUISTIC_TYPE_REF" of each tier. Their hierarchy
can assume any order/format, it's the user choice.

.. code-block:: xml

    <header>
        <data_structure>
            <hierarchy>['utterance', 'words']</hierarchy>
        <data_structure>
        <tier_mapping>
            <type name="words">
                <tier>W-Words</tier>
            </type>
            <type name="utterance">
                <tier>K-Spch</tier>
                <tier>W-Spch</tier>
            </type>
        </tier_mapping>
    </header>

The Elan file contains a lot of information that is only used by the program itself and is not to much use for the GrAF.
Only the TIERs and TIME_ORDER information are usefully to the Poio API the rest will be stored in a metafile under
the tag *miscellaneous*.
The metafile will be named with a extension "-extinfo.xml".

Metafile example:

.. code-block:: xml

    <metadata xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <header>
            <data_structure>
                <hierarchy>['utterance', 'words',...]</hierarchy>
            <data_structure>
            <tier_mapping>
                <type name="gesture_meaning">
                    <tier>W-RGMe</tier>
                    <tier>K-RGMe</tier>
                </type>
                [.......]
            </tier_mapping>
        </header>
        <file data_type="Elan file">
            <miscellaneous>
            <ANNOTATION_DOCUMENT AUTHOR="" DATE="2006-06-13T15:09:43+01:00" FORMAT="2.3" VERSION="2.3"
            xsi:noNamespaceSchemaLocation="http://www.mpi.nl/tools/elan/EAFv2.3.xsd"/>
            [.........]
            </miscellaneous>
        </file>
    </metadata>

*Relation between the elan tier elements and GrAF ISO:*
  * Nodes are going to use the same id as the TIERs followed by "-n" and an sequential index. E. g. ("W-RGph-n233").
  * The regions anchors will be derived from the map TIME_ORDER. The region id is like the node id but instead of the "-n" is a "-r". E. g. (W-RGph-r233)
  * The values of ALIGNABLE_ANNOTATION and REF_ANNOTATION will be the annotation values under the tag *a* and the id exactly the same. E. g. (a233)

**Imporant references:**
  * Elan Format (http://www.mpi.nl/tools/elan/EAF_Annotation_Format.pdf)
  * Elan Information (http://tla.mpi.nl/tools/tla-tools/elan/elan-description/)
  * Elan Tools and Documentation (http://tla.mpi.nl/tools/tla-tools/elan/download/)

^^^^^^^^^^^^^^^^^^^^^^^^^^
How to use the elan parser
^^^^^^^^^^^^^^^^^^^^^^^^^^

First is important to know the class DataStructureTypeWithConstraints. This class contains the data structure hierarchy
and the dictionary with the constraints.

For the parser works properly is need to set the data structure of the class first:

.. code-block:: python

    # Initialize
    data_hierarchy = ['utterance','words','part_of_speech']

    # Path to the elan file
    inputfile = 'example.elan'

    elan_graf = elan.Elan(inputfile, data.DataStructureTypeWithConstraints(data_hierarchy))

**Note:** If a data structure isn't given the API will assume the structure of the elan tiers.

Next to create a GrAF object:

.. code-block:: python

    graph = elan_graf.elan_to_graf()

Now it's possible to access it with `Graf-python API <https://github.com/cidles/graf-python>`_

For more information about Graf-python (https://graf-python.readthedocs.org/en/latest/howto.html)

Generate the GrAF files:

.. code-block:: python

    elan_graf.generate_graf_files()

This step will generate the GrAF files inclunding the header and the metafile.

**Note:** To create the GrAF files it's first needed to run the method above described.


------------------
Other file formats
------------------

Under development ...

=========
Resources
=========

Source Files:
  * :download:`pickle2graf.py<_resources/pickle2graf.py>`
  * :download:`elan2graf.py<_resources/elan2graf.py>`

