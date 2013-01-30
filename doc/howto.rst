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

===================================
Structure of GrAF files in Poio API
===================================

This section explains how is the relation between the GrAF structure files with Poio API.

| The header file will always have the same name as the original file with the extension *.hdr*.
| E. g. assuming that the original file was example.txt the header file will be *example.hdr*.

| The header file will contain information that forms the GrAF. Some of that information may be consulted in detail in the references link.
| For Poio API the important part will be only the dataDesc.

.. code-block:: xml

    [.......]
      <dataDesc>
        <primaryData f.id="text" loc="example.txt">
          <annotations>
            <annotation f.id="utterance" loc="example-utterance.xml"/>
            <annotation f.id="word" loc="balochi-word.xml"/>
            <annotation f.id="translation" loc="balochi-translation.xml"/>
          </annotations>
        </primaryData>
      </dataDesc>
    [.......]

The *primaryData* provides the location of the primary data document:

* loc - Is the identification of the primary data document.
* f.id - Is the file type of the primary data document.

.. code-block:: xml

    <primaryData f.id="text" loc="example.txt">

The *annotations* are the tiers associated to the primary data document:

* loc - Is the identification of the tier document.
* f.id - Is the file type of the tier document.

.. code-block:: xml

  <annotations>
    <annotation f.id="utterance" loc="example-utterance.xml"/>
    <annotation f.id="word" loc="balochi-word.xml"/>
    <annotation f.id="translation" loc="balochi-translation.xml"/>
  </annotations>

In Poio API those tiers are linked to the elements of the data structure. This allows the
correlation between the hierarchical structure of Poio API and the structure of Graf to be possible. Each one of those
tiers will only contain the information relating to each of the elements of the data structure. By doing this it
immediately gets the dependency between the tiers.

The creation of those tiers(*annotations*) will always be the name of the original file followed by an hyphen an by the
respective data structure element, **filename-data_element.xml** (e. g. example-utterance.xml). Their type always going
to be the name of the respective data structure element.

There will be generic two kinds of files. Some files that have nodes and whether or without annotations and other
files that will have only annotations. This is due to the fact that we assume that the first elements of a hierarchical
list are nodes may thus contain one or more annotations. While the remaining elements of the list will be considered
only as annotations of values ​​and/or annotations of reference to another node or annotation.

Below a simple example explaining everything it's shown.

Assuming that the original file is *example.txt* and the data structure hierarchy is like this:

.. code-block:: python

	[ 'word', 'translation' ]

The generated GrAF files should be two:

* example-word.xml
* example-translation.xml

In this example since the *node* element it's the first in the hierarchy it'll be generated a file with the nodes of
the word and a file only with annotation of the *translation* element. The *translation* annotation will point to a node
of *word* because it's parent in the hierarchy.

The result files should be like this:

* For the *word*:

    .. code-block:: xml

        <graph xmlns="http://www.xces.org/ns/GrAF/1.0/">
          <graphHeader>
            <labelsDecl/>
            <dependencies/>
            <annotationSpaces>
              <annotationSpace as.id="word"/>
            </annotationSpaces>
          </graphHeader>
          <node xml:id="word-n0">
            <link targets="word-r0"/>
          </node>
          <region anchors="0 10" xml:id="word-r0"/>
          <a as="word" label="word" ref="word-n0" xml:id="word-a0">
            <fs>
              <f name="annotation_value">Ola CIDLeS</f>
            </fs>
          </a>
        [........]

* For the *translation* it's going to have a dependency as you can see in the *<dependencies>*:

    .. code-block:: xml

        <graph xmlns="http://www.xces.org/ns/GrAF/1.0/">
          <graphHeader>
            <labelsDecl/>
            <dependencies>
              <dependsOn f.id="word"/>
            </dependencies>
            <annotationSpaces>
              <annotationSpace as.id="translation"/>
            </annotationSpaces>
          </graphHeader>
          <a as="translation" label="translation" ref="word-n0" xml:id="translation-a0">
            <fs>
              <f name="annotation_value">Hello CIDLeS</f>
            </fs>
          </a>
        [........]


**References:**
  * GrAF ISO standards (http://www.iso.org/iso/catalogue_detail.htm?csnumber=37326)

===============================================
Transformation of file formats from and to GrAF
===============================================

This section explains how to transformation a specific kind of file into GrAF ISO standards files.

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
  * Nodes ids are going to use a prefix that's the "LINGUISTIC_TYPE_REF" and then the same id as the TIERs followed by "/n" and a sequential index. E. g. ("gestures/W-RGph/n233").
  * The regions anchors will be derived from the map TIME_ORDER. The region id is like the node id but instead of the "/n" is a "/r". E. g. (W-RGph-r233)
  * The values of ALIGNABLE_ANNOTATION and REF_ANNOTATION will be the annotation values under the tag *a* and the id exactly the same. E. g. (a233)

**References:**
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

==============================
Example transformation scripts
==============================

Files on Github:
  * `pickle2graf.py <https://github.com/cidles/poio-api/blob/master/examples/pickle2graf.py>`_
  * `elan2graf.py <https://github.com/cidles/poio-api/blob/master/examples/elan2graf.py>`_

