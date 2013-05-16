**************************************************
How to wrote a Parser/Writer for a new file format
**************************************************

In order to create a parser with PoioAPI is necessary to implement the base 
class "BaseParser".

The base class contains five abstract methods that will allow the GrAF converter to
make the parsing of the files correctly. The five methods are:

* get_root_tiers() - Get all the root tiers.
* get_child_tiers_for_tier(tier) - Get the child tiers of a particular tier.
* get_annotations_for_tier(tier, annotation_parent) - Get the annotations of a certain tier.
* tier_has_regions(tier) - Verify if a specific tier contains regions.
* region_for_annotation(annotation) - Get the region for a specific annotation.

*Note: All the methods must be implemented otherwise it will be raised an exception.*

The tiers and the annotations should inherit from the classes poioapi.io.graf.Tier and
poioapi.io.graf.Annotation respectively.

Each Tier is defined with a name and with a annotation_space (which is None by default), but in
some cases it might be necessary to create a subclass of it with more characteristics. E. g. the
Elan structure use the "linguistic_type" to distinguish the tiers type. So a new Tier class could
be like this:

.. code-block:: python

    class ElanTier(poioapi.io.graf.Tier):
        __slots__ = ["linguistic_type"]

        def __init__(self, name, linguistic_type):
            self.name = name
            self.linguistic_type = linguistic_type
            self.annotation_space = linguistic_type

The annotation_space represents a group of a Tier with the same characteristics. If the annotation_space
of a Tier is None the GrAF converter will assume that the annotation_space is the same as Tier name.

Each Annotation is defined with a unique id and can contain a value and features. The features are
dictionaries with additional or essential information to the annotation and will be in the
feature_structure of the annotation in GrAF representation.

Classes and Documentation:

* :py:class:`poioapi.io.graf.BaseParser`
* :py:class:`poioapi.io.graf.Tier`
* :py:class:`poioapi.io.graf.Annotation`


==============================================
Writing a parser to transform a file into GrAF
==============================================

The transformation of the file into GrAF will be done by the poioapi.io.graf.GrAFConverter.
This class it will use the parser methods to retrieve the information from the file. So the conversion
it will rely mainly in the parser.

To write the parser is need to create a subclass of poioapi.io.graf.BaseParser:

.. code-block:: python

    class SimpleParser(poioapi.io.graf.BaseParser):
    
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
            

In this example we will assume that the tiers will be the elements in the **tiers**
list. For each of those tiers there will be a list with the respective data:

.. code-block:: python

    class SimpleParser(poioapi.io.graf.BaseParser):

        tiers = ["utterance", "word", "wfw", "graid"]
        
        utterance_tier = ["This is a utterance", "that is another utterance"]
        
        word_tier = [['This', 'is', 'a', 'utterance'], ['that', 'is', 'another', 'utterance']]
        
        wfw_tier = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        
        graid_tier = ['i', 'j', 'k', 'l', 'm', 'n', 'o', 'p']
    
        def __init__(self):
            pass
            
        [...]

See `Methods Implementation`_ for more detailed information.

Using the parser to convert the new file format into GrAF:

.. code-block:: python

    parser = SimpleParser()

    converter = poioapi.io.graf.GrAFConverter(parser)
    converter.convert()

    graph = converter.graph

Classes and Documentation:

* :py:class:`poioapi.io.graf.GrAFConverter`

----------------------
Methods Implementation
----------------------

Starting with the ``get_root_tiers`` method. This method has the aim of return 
all the elements that are considered the roots of a data hierarchy and that 
contains the main data. In this case the root tier will be the "utterance".

.. code-block:: python
        
        def get_root_tiers(self):
            return [poioapi.io.graf.Tier("utterance")]    
            
The method ``get_child_tiers_for_tier`` is intended to return all child tiers of 
a a given tier. With this example we assume that the children of the "utterance" 
tier would be the "word" and that for these tier there children would be 
"graid" and "wfw".

.. code-block:: python

    def get_child_tiers_for_tier(self, tier):
        if tier.name == "utterance":
            return [poioapi.io.graf.Tier("word")]
        if tier.name == "word":
            return [poioapi.io.graf.Tier("graid"), poioapi.io.graf.Tier("wfw")]

        return None
        
**Note:** This two methods should always return a list with tiers type elements 
or None.

The method ``get_annotations_for_tier`` is used to collect the annotations for a
particular tier. The annotations will be in the end the data/values ​​which are 
connected to this tier. Following the example is shown that annotations/values​​/data 
of each tier are the lists with the same name.

.. code-block:: python

    def get_annotations_for_tier(self, tier, annotation_parent=None):
        if tier.name == "utterance":
            return [poioapi.io.graf.Annotation(i, v) for i, v in enumerate(self.utterance_tier)]

        [...]

Some of the tiers are children tiers and their annotations will also
undergo of that hierarchy. One of the parameters of this method is the 
``annotation_parent`` (Annotation type). This parameter will serve to filter 
exactly which are the annotations ("children" annotations) to return of a 
certain tier.

.. code-block:: python

        [...]
        
        if tier.name == "word":
            return [poioapi.io.graf.Annotation(2 + 4 * annotation_parent.id + i, v) for i, v
                    in enumerate(self.word_tier[annotation_parent.id])]

        if tier.name == "graid":
            return [poioapi.io.graf.Annotation(annotation_parent.id + 10, self.graid_tier[annotation_parent.id - 2])]

        if tier.name == "wfw":
            return [poioapi.io.graf.Annotation(annotation_parent.id + 12, self.wfw_tier[annotation_parent.id - 2])]

        return []

**Note:** This method should always return a list with annotation type elements 
or an empty list.

The method ``tier_has_regions`` helps to understand which tiers contains regions. 
These regions are mainly intervals. The intervals could be: intervals of time; 
a range in the text or in a line; a range of characters; etc.

.. code-block:: python

    def tier_has_regions(self, tier):
        
        if tier.name == "utterance":
            return True
            
        return False
        
To get the regions of a annotation it should be used the method 
``def region_for_annotation``. This method must return a ``tuple`` with 
the regions. In our example the tier with regions is the "utterance". 
So the regions for the first annotation from the tier "utterance" should be 
``(0, 19)``.

.. code-block:: python

    def region_for_annotation(self, annotation):
        
        if self.last_region == 0:
            part_1 = 0
        else:
            part_1 = self.last_region[0]
            
        part_2 = len(annotation.value) - 1
        
        region = (part_1, part_2)

        self.last_region = region
        
        return region