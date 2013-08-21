.. _parserwriter_howto:

How to write a Parser/Writer for a new file format
**************************************************

In order to support your own file format in Poio API you need implement your
own parser as a sub-class of the base class
:py:class:`poioapi.io.graf.BaseParser`. The base class contains six abstract
methods that will allow the GrAF converter to build a GrAF object from the
content of your files. The six methods are:

* get_root_tiers() - Get the root tiers.
* get_child_tiers_for_tier(tier) - Get the child tiers of a give tier.
* get_annotations_for_tier(tier, annotation_parent) - Get the annotations on a
  given tier.
* tier_has_regions(tier) - Check if the annotations on a given tier specify
  regions.
* region_for_annotation(annotation) - Get the region for a given annotation.
* get_primary_data() - Get the primary data that the annotations refer to.

*Note: All the methods must be implemented otherwise it will be raised an
exception.*

The tiers and annotations that are passed to the methods are normally objects
from the classes :py:class:`poioapi.io.graf.Tier` and
:py:class:`poioapi.io.graf.Annotation`. If you need to pass additional
information between the methods, that are not present in our implementation
of the classes, you might also sub-class ``Tier`` and/or ``Annotation`` and add
your own properties. **By sub-classing you make sure that the properties from
our implementation are still there. The converter needs them to build the GrAF
object.**

Each ``Tier`` contains a `name` and an `annotation_space` property (the latter
is `None` by default). The class ``ElanTier`` exemplifies the sub-classing of
`Tier`. In the case of Elan we need to store an additional property
`linguistic_type` to be able to implement the complete parser:

.. code-block:: python

    class ElanTier(poioapi.io.graf.Tier):
        __slots__ = ["linguistic_type"]

        def __init__(self, name, linguistic_type):
            self.name = name
            self.linguistic_type = linguistic_type
            self.annotation_space = linguistic_type

``Tier`` s use the `annotation_space` to describe that they share certain
annotation types. If the `annotation_space` is `None` the GrAF converter
will use the `name` as the label for the annotation space.

Each ``Annotation`` is defined with a unique `id` property and can contain a
`value` and a ' features` property. Features are stored in a dictionary with
and will be stored in the `feature_structure` of the annotation in the GrAF
representation.

**References:**

* :py:class:`poioapi.io.graf.BaseParser`
* :py:class:`poioapi.io.graf.Tier`
* :py:class:`poioapi.io.graf.Annotation`


Example: A simple parser based on static data
=============================================

The transformation of annotation data to GrAF is done by the class
:py:class:`poioapi.io.graf.GrAFConverter`. This class it will use the parser's
methods to retrieve the information from the file.

Sub-classing from BaseParser
----------------------------

First we will sub-class our own parser ``SimpleParser`` from the class
:py:class:`poioapi.io.graf.BaseParser` with empty methods. We will set some
static data within the class that represent our tier names
and the annotations for each tier:

.. code-block:: python

    class SimpleParser(poioapi.io.graf.BaseParser):
    
        tiers = ["utterance", "word", "wfw", "graid"]
        utterance_tier = ["This is a utterance", "that is another utterance"]
        word_tier = [['This', 'is', 'a', 'utterance'], ['that', 'is', 'another',
                      'utterance']]
        wfw_tier = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        graid_tier = ['i', 'j', 'k', 'l', 'm', 'n', 'o', 'p']

        def __init__(self):
            pass
    
        def get_root_tiers(self):
            pass

        def get_child_tiers_for_tier(self, tier):
            pass
            
        def get_annotations_for_tier(self, tier, annotation_parent=None):
            pass

        def tier_has_regions(self, tier):
            pass
            
        def region_for_annotation(self, annotation):
            pass    

        def get_primary_data(self):
            pass

If your annotations are stored in a file then you need to implement your own
strategy how to load the file's content into your parser class. The
``__init__()`` of your parser class might be a good place to load your file.

**References:**

* :py:class:`poioapi.io.graf.GrAFConverter`


Implementation of the parser methods
------------------------------------

We will start with the ``get_root_tiers()`` method. This method will return all
the root tiers as objects of the class ``Tier`` (or a sub-class of it). In our
case this is only the utterance tier:

.. code-block:: python
        
    def get_root_tiers(self):
        return [poioapi.io.graf.Tier("utterance")]    
            
The method ``get_child_tiers_for_tier()`` returns all child tiers of 
a given tier, again as ``Tier`` objects. In our simple example we assume that
the child of the utterance tier is the word tier and the word tier has the
children graid and wfw:

.. code-block:: python

    def get_child_tiers_for_tier(self, tier):
        if tier.name == "utterance":
            return [poioapi.io.graf.Tier("word")]
        if tier.name == "word":
            return [poioapi.io.graf.Tier("graid"), poioapi.io.graf.Tier("wfw")]

        return None
        
**Note:** This two methods must always return a list of ``Tier`` objects or
`None`.

The method ``get_annotations_for_tier()`` is used to collect the annotations
for a given tier. Each annotation must at least cotain a unique `id` and an
annotation `value`. Both properties are already present in the class
``Annotation`` that we use here to return the annotations. For the utterance
tier we can simply convert the list of strings in our `self.utterance_tier`
data store:

.. code-block:: python

    def get_annotations_for_tier(self, tier, annotation_parent=None):
        if tier.name == "utterance":
            return [poioapi.io.graf.Annotation(i, v)
                        for i, v in enumerate(self.utterance_tier)]

            [...]

For all tiers that are children of another tier the annotations within the tiers
are normally also children of another annotation on the parent tier. In this
case the ``Converter`` will pass a value in the parameter `annotation_parent`.
In our case, the `id` of the parent annotation points to the location of the
child annotations in the lists `self.word_tier`, `self.graid_tier` and
`self.wfw_tier`:

.. code-block:: python

    [...]
        
        if tier.name == "word":
            return [poioapi.io.graf.Annotation(2 + 4 * annotation_parent.id + i, v) for i, v
                    in enumerate(self.word_tier[annotation_parent.id])]

        if tier.name == "graid":
            return [poioapi.io.graf.Annotation(
                annotation_parent.id + 10, self.graid_tier[annotation_parent.id - 2])]

        if tier.name == "wfw":
            return [poioapi.io.graf.Annotation(
                annotation_parent.id + 12, self.wfw_tier[annotation_parent.id - 2])]

        return []

**Note:** This method must always return a list with ``Annotation`` elements 
or an empty list.

The method ``tier_has_regions()`` describes which tiers contain regions. 
These regions are intervals that refer to the primary data. Depending on the
type of the primary data the regions can encode intervals of time (encoded
as milliseconds, in most cases) or a range in a string (from start to end
position). In our case we assume that only the root tier `utterance` is
connected to the primary data via regions:

.. code-block:: python

    def tier_has_regions(self, tier):
        
        if tier.name == "utterance":
            return True
            
        return False
        
To get the regions of a specific annotation the ``Converter`` will call the
method ``region_for_annotation()``. This method must return a tuple with 
start and end of the regions. In our example the tier with regions is the
utterance tier.  So the region for the first utterance is ``(0, 19)``, if we
assume that we want to return the content of the two utterances connected
with a blank " " as the primary data. We can simply calculate the regions from
the length of the strings in ``self.utterance_tier``:

.. code-block:: python

    def region_for_annotation(self, annotation):
        
        if annotation.id == 0:
            return (0, len(self.utterance_tier[0]))
        elif annotation.id == 1:
            return (len(self.utterance_tier[0]) + 1,
                    len(self.utterance_tier[0]) + 1 + len(self.utterance_tier[1]))

Last but not least we also have to return the primary data. As the utterance
tier was the root tier and we already defined the regions for the utterance
annotations based on the strings in ``self.utterance_tier`` we can simply join
the two strings and return the result as the primary data:

.. code-block:: python

    def get_primary_data(self):
        return ' '.join(self.utterance_tier)


Using the parser to convert to GrAF
-----------------------------------

You can now use the ``SimpleParser`` class to convert the static data into
a GrAF object:

.. code-block:: python

    parser = SimpleParser()

    converter = poioapi.io.graf.GrAFConverter(parser)
    converter.parse()

    graf = converter.graf

The `converter` object contains two more objects that contain information
from the parsed data:

* The tier hierarchies is stored in `converter.tier_hierarchies`.
* The primary data for the annotations is stored in `converter.primary_data`.

If you want to write the data to GrAF files you have to create a GrAF writer
object and pass it to the `Converter`'s constructor:

.. code-block:: python

    parser = SimpleParser()
    writer = poioapi.io.graf.Writer()

    converter = poioapi.io.graf.GrAFConverter(parser, writer)
    converter.parse()
    converter.write("simple.hdr")

The section :ref:`excel_parser` discusses a slightly more complex use case: how to
write a parser for custom annotations stored in a Microsoft Excel file.
