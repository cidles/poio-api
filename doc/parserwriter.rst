**************************************************
How to wrote a Parser/Writer for a new file format
**************************************************

In order to create a parser with PoioAPI is necessary to implement the base 
class "BaseParser". This a abstract class (interface) that contains the abstract 
methods needed to be implemented to the proper functioning of the parser and 
to be able to convert the data to GrAF format.

This base class has five abstract methods that must be implemented. Of these 
five methods three of them (get_root_tiers, get_child_tiers_for_tier and 
get_annotations_for_tier) should at least returns an empty list while the 
other two (tier_has_regions and region_for_annotation) may simply do 
nothing(*pass*).
All the methods must be implemented otherwise it will be raised an exception.

It is necessary to have in mind that each format is different in its construction. 
So the user will be responsible for defining / choosing what and which data 
considered important.

Apart from BaseParser class must also have the knowledge of the classes Tier
and Annotation.
The class Tier is a list of tiers. Each tier is represented at least with a 
name and can have in addition also a type or linguistic.
The class Annnotation is a list of annotations. Each annotation is 
represented by an id and can contain a value and features.

Note that the methods from the BaseParser base class shall only use and return
Tiers and Annotations types values.

Classes and Documentation:

* :py:class:`poioapi.io.graf.BaseParser`
* :py:class:`poioapi.io.graf.Tier`
* :py:class:`poioapi.io.graf.Annotation`


==============================================
Writing a parser to transform a file into GrAF
==============================================

First create a class based on the BaseParser interface and create all the 
interface required methods.

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