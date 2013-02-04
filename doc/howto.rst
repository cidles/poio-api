*******************
How To Use Poio API
*******************

============
Introduction
============

Poio API provides access to language documentation data and a wide range of annotations schemes stored in different file
formats. It's based on a common and standardized representational format: annotation graphs as defined by "ISO 24612 -
Language resource management -- Linguistic annotation framework (LAF)". The data and annotations can then be used
with existing NLP tools and workflows and hence be combined with any other data source that is isomorphic to the
representations in this framework.

**References:**
  * ISO 24612 (http://www.iso.org/iso/catalogue_detail.htm?csnumber=37326)

.. _data_structure_types:

====================
Data Structure Types
====================

We use a data type called data structure type to represent annotation schemes in a tree. A simple data structure
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

In Poio API there are several data structure types pre-defined as classes in the module `poioapi.data`, for example:

* :py:class:`poioapi.data.DataStructureTypeGraid`
* :py:class:`poioapi.data.DataStructureTypeMorphsynt`

The user of the API can of course create her own data structure type, by deriving a custom class from the base class
`poioapi.data.DataStructureType`. This is often done when a GrAF graph was created from an ELAN file that contains
custom tiers. A custom class would look like this:

.. code-block:: python

  class DataStructureTypeElan(poioapi.data.DataStructureType):
      name = "ELAN"

      data_hierarchy =\
      [ 'utterance', 'phonetic_transcription',
          [ 'words', 'part_of_speech' ]
      ]


=================
Annotation Graphs
=================

TODO

.. _graf_structure:

===================================
Structure of GrAF files in Poio API
===================================

TODO

**References:**
  * ISO 24612 (http://www.iso.org/iso/catalogue_detail.htm?csnumber=37326)


===============================================
Transformation of file formats from and to GrAF
===============================================

----------------
Elan's EAF files
----------------

Elan is a widely used transcription and annotation software developed at the
Max-Planck-Institute in Nijmegen. Due to its popularity the file format used
by Elan, an XML format called "EAF" ("Elan Annotation Standard"), has become
the de facto standard in language documentation and is used by several project
in qualitative and quantitative language typology. Poio API fully supports to
convert EAF files to GrAF annotation graphs and back again without any loss of
information.

Basically, Poio API extracts all `<annotation>` tags from the EAF file and
converts them to GrAF nodes and annotations. The `<time_slot>` tags in the
EAF file are used to create the regions for the nodes in GrAF. The rest of the
EAF file is left intact and stored as a separate file `prefix-extinfo.xml` in
parallel to the other GrAF files as described in section :ref:`graf_structure`
(where `prefix` is again the base name of the header file of GrAF). In addition
to this, the original EAF file is also stored together with the GrAF files.

The structure of the GrAF files is defined by the tier hierarchy in the Elan
file. As an example we will use the example data file that you may `download from
the the Elan website <http://tla.mpi.nl/tools/tla-tools/elan/download/>`_ (next
to "Example Set"). If you open those files in Elan and sort the tiers by
hierarchy you will have the following tier hierarchy:

.. image:: _static/elan_tier_hierarchy.png

In this case, there are four *root tiers* with annotations: `K-Spch`, `W-Spch`,
`W-RGU` and `K-RGU`. The latter three each has several child tiers. Each tier
has a *linguistic type*, which you can see if you click on `Tier` -> `Change
Tier Attributes...`:

.. image:: _static/elan_tier_attributes.png

In this case the tier `K-Spch` has the linguistic type `utterance`, and so on.
These linguistic types correspond to the names in the data structure types of
Poio API (see section :ref:`data_structure_types`). Which means that if you
transform an EAF file into GrAF files with Poio API it will create one file for
each of the linguistic types. Each of those files file will contain all the
annotations of all the tiers that have the corresponding linguistic type. In
our example, Poio API will create one file `prefix-utterance.xml` that contain
the annotations from the tiers `K-Spch` and `W-Spch`. The file
`prefix-words.xml` will then contain all annotations from tier `W-Words` with
links to the parent annotations in `prefix-utterance.xml`. You can find an
example of the GrAF structure for the sample EAF file `on Github
<https://github.com/cidles/poio-api/tree/master/src/poioapi/tests/sample_files/elan_graf>`_.

The first annotation of the tier `W-Spch` with the annotation value
"so you go out of the Institute to the Saint Anna Straat." looks like this in
GrAF:

.. code-block:: xml

  <node xml:id="utterance/W-Spch/n8">
    <link targets="utterance/W-Spch/r8"/>
  </node>
  <region anchors="780 4090" xml:id="utterance/W-Spch/r8"/>
  <a as="utterance" label="utterance" ref="utterance/W-Spch/n8" xml:id="a8">
    <fs>
      <f name="annotation_value">so you go out of the Institute to the Saint Anna Straat.</f>
      <f name="time_slot2">ts23</f>
      <f name="time_slot1">ts4</f>
    </fs>
  </a>

The `<node>` is linked to a `<region>` that contains the values of the time slots of
the original EAF file. The annotation `<a>` for the node has a feature structure
`<fs>` with three features `<f>` for the annotation value and the original names
of the time slots. We need to save the names of the time slots to be able to
reconstruct the original EAF file.

The first annotation of `W-Spch` in `prefix-words.xml` looks like this:

.. code-block:: xml

  <node xml:id="words/W-Words/n23">
    <link targets="words/W-Words/r23"/>
  </node>
  <edge from="utterance/W-Spch/n8" to="words/W-Words/n23" xml:id="e23"/>
  <region anchors="780 1340" xml:id="words/W-Words/r23"/>
  <a as="words" label="words" ref="words/W-Words/n23" xml:id="a23">
    <fs>
      <f name="annotation_value">so</f>
      <f name="time_slot2">ts6</f>
      <f name="time_slot1">ts4</f>
    </fs>
  </a>

The node for the word annotation is similar to the utterance node, except for an
additional `<edge>` tag that links the node to the corresponding utterance node.
Nodes and edges are created for all annotations of tiers that have time slots
*and* a parent tier in EAF (those tiers have the stereotype `"Time Subdivision"`
in EAF).

For tiers that have a parent tier but *no regions* Poio API only creates
annotations that refer to the node in the parent tier (stereotypes `"Symbolic
Association"` in EAF). For example, the tier `W-POS` in the sample has no time
slots and is of the stereotype `Symbolic Association`. An annotation in GrAF in
`prefix-part_of_speech.xml` then looks like this:

.. code-block:: xml

  <a as="part_of_speech" label="part_of_speech" ref="words/W-Words/n23" xml:id="a120">
    <fs>
      <f name="ref_annotation">a23</f>
      <f name="annotation_value"/>
    </fs>
  </a>


**References:**
  * EAF Format (http://www.mpi.nl/tools/elan/EAF_Annotation_Format.pdf)
  * Information about Elan (http://tla.mpi.nl/tools/tla-tools/elan/elan-description/)
  * Elan Tools and Documentation (http://tla.mpi.nl/tools/tla-tools/elan/download/)


==============================
Example transformation scripts
==============================

Files on Github:
  * `pickle2graf.py <https://github.com/cidles/poio-api/blob/master/examples/pickle2graf.py>`_
  * `elan2graf.py <https://github.com/cidles/poio-api/blob/master/examples/elan2graf.py>`_

