Introduction to Poio API
************************

Poio API is a free and open source Python library to access and search data
from language documentation in your linguistic analysis workflow. It converts
file formats like Elan's EAF, Toolbox files, Typecraft XML and others into
annotation graphs as defined in ISO 24612. Those graphs, for which we use
an implementation called "Graph Annotation Framework" (GrAF), allow unified
access to linguistic data from a wide range sources.

Think of GrAF as an assembly language for linguistic annotation, then Poio API
is a libray to map from and to higher-level languages.

Poio API is developed as a part of the `curation project of the F-AG 3 within
CLARIN-D <http://de.clarin.eu/en/discipline-specific-working-groups/wg-3-linguistic-fieldwork-anthropology-language-typology/curation-project-1.html>`_.

**References:**
  * ISO 24612: http://www.iso.org/iso/catalogue_detail.htm?csnumber=37326
  * Graph Annotation Framework (GrAF): http://www.xces.org/ns/GrAF/1.0/

.. _data_structure_types:


Quick Example
=============

This block of code loads a Elan EAF file as annotation graph and writes the data
as html table into a file:

.. code-block:: python

  # imports
  import poioapi.annotationgraph
  import poioapi.data

  # Create an empty annotation graph
  ag = poioapi.annotationgraph.AnnotationGraph(None)
  # Load the data from EAF file
  ag.from_elan("elan-example3.eaf")
  # Set the structure type for hierarchical/interlinear output
  ag.structure_type_handler = poioapi.data.DataStructureType(
      ag.tier_hierarchies[0])

  # Output as html
  import codecs
  f = codecs.open("example.html", "w", "utf-8")
  f.write(ag.as_html_table(False, True))
  f.close()

To try it out you may download the `example file from the Elan homepage
<http://tla.mpi.nl/tools/tla-tools/elan/download/>`_.


Data Structure Types
====================

We use a data type called `DataStructureType` to represent annotation schemes
in a tree. A simple data structure type describing that the researcher wants to
tokenize a text into words before adding a word-for-word translation and a
translation for the whole utterance looks like this:

.. code-block:: python

	[ 'utterance', [ 'word', 'wfw' ], 'translation' ]

A slightly more complex annotation schema is GRAID (Grammatical Relations and
Animacy in Discourse), developed by Geoffrey Haig and Stefan Schnell. GRAID adds
the notion of clause units as an intermediate layer between utterance and word
and three more annotation tiers on different levels:

.. code-block:: python

	[ 'utterance',
		[ 'clause unit',
			[ 'word', 'wfw', 'graid1' ],
		'graid2' ],
	  'translation', 'comment' ]

One advantage in representing annotation schemes through those simple trees, is
that the linguists instantly understand how such a tree works and can give a
representation of "their" annotation schema. In language documentation and
general linguistics researchers tend to create ad-hoc annotation schemes fitting
their background and then normally start to create only those annotations
related to their current research project. This is for example reflected in an
annotation software like ELAN, where the user can freely create tiers with any
names and arrange them in custom hierarchies. As we need to map those data into
our internal representation, we try to ease the creation of custom annotation
schemes that are easy to understand for users. For this we will allow users to
create their own data structure types and derive the annotation schemes for
GrAF files from those structures.

In Poio API there are several data structure types pre-defined as classes in
the module `poioapi.data`, for example:

* :py:class:`poioapi.data.DataStructureTypeGraid`
* :py:class:`poioapi.data.DataStructureTypeMorphsynt`

The user of the API can of course create her own fixed data structure type, by
deriving a custom class from the base class `poioapi.data.DataStructureType`.
In you workflow you might also create an object with your own tier hierarchy
by passing a list of lists (as in the examples above) when creating an object
from `DataStructureType`:

.. code-block:: python

  import poioapi.data
  
  my_data_structure = poioapi.data.DataStructureType(
      [ 'utterance', [ 'word', 'wfw' ], 'translation' ])

If you create an annotation graph from one of the supported file formats, the
hierarchies that are present in file are accesible via the `tier_hierarchies`
property of the annotation graph object. As an example, we use the `example
file from the Elan homepage
<http://tla.mpi.nl/tools/tla-tools/elan/download/>`_:

.. code-block:: python

  import poioapi.annotationgraph

  ag = poioapi.annotationgraph.AnnotationGraph()
  ag.from_elan("elan-example3.eaf")
  print(ag.tier_hierarchies)


Which will output:

.. code-block:: python

  [['utterance..K-Spch'],
   ['utterance..W-Spch',
    ['words..W-Words', ['part_of_speech..W-POS']],
    ['phonetic_transcription..W-IPA']],
   ['gestures..W-RGU', ['gesture_phases..W-RGph', ['gesture_meaning..W-RGMe']]],
   ['gestures..K-RGU', ['gesture_phases..K-RGph', ['gesture_meaning..K-RGMe']]]]

This is a list of tier hierarchies. In this case, there are two hierarchies in
the .eaf file, one which has the root tier `utterance..K-Spch` and another one
with root tier `utterance..W-Spch`.

The user can now easily create an instance of the class `DataStructureType`
with one of the hierarchies. This will then be the default hierarchy for all
subsequent actions on the annotation graph (e.g. queries, HTML output, etc.):

.. code-block:: python

  ag.structure_type_handler = poioapi.data.DataStructureType(
      ag.tier_hierarchies[0])


Annotation Graphs
=================

TODO

.. _graf_structure:


Structure of GrAF graphs in Poio API
====================================

TODO


