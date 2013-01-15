************
Elan Handler
************

This is the documentation how the Elan files are parsed in Python Library Poio API.

Introduction
============

In order to convert the Elan files into GrAF object or GrAF files there is going to be necessary to understand the use of the data structures hierarchy and the metafile. This data structure will have a special role in the creation of the GrAF because is going to contain the dependencies between the elements tiers each means the dependencies of the many parts in the graph.
The data structure elements is going to have the same names as the "LINGUISTIC_TYPE_REF" of each tier. Their hierarchy can assume any order/format, it's the user choice. 

Data Structure Hierarchy example:
.. code-block:: python
    ['utterance', 
        ['words', 
            ['part_of_speech', 
                ['phonetic_transcription']]], 
    'gestures']

The Elan file contains a lot of information that is only used by the program itself and is not to much use for the GrAF. Thereby is important to separate the information that's will be used in the GrAF construction that are merely the TIERs and the rest will be stored in the file so that later it can be possible to rebuild the elan file again.
The metafile is structure is composed by the header file, data structure hierarchy, type of file (text, elan, etc...) and miscellaneous information. 

Metafile example
.. code-block:: python
    <metadata xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      <header_file>example</header_file>
      <data_structure_hierarchy>
        <hierarchy>['utterance', 'words',...]</hierarchy>
        <constraints>
          <constraint words="['W-Words']"/>
          .......
        </constraints>
      </data_structure_hierarchy>
      <file data_type="Elan file">
        <miscellaneous>
          <ANNOTATION_DOCUMENT AUTHOR="" DATE="2006-06-13T15:09:43+01:00" FORMAT="2.3" VERSION="2.3" xsi:noNamespaceSchemaLocation="http://www.mpi.nl/tools/elan/EAFv2.3.xsd"/>
          .............      
          </miscellaneous>
      </file>
    </metadata>

In the data structure hierarchy tag exist a child "constraints". Those constraints are the the tiers id that belongs to an element in the hierarchy.

Tag "data_structure_hierarchy" constraints example:
.. code-block:: python
    <data_structure_hierarchy>
        <hierarchy>['utterance', 'words']</hierarchy>
        <constraints>
            <constraint words="['W-Words']"/>
            <constraint utterance="['K-Spch', 'W-Spch']"/>
        </constraints>
    </data_structure_hierarchy>

Important references:
* Elan Format (http://www.mpi.nl/tools/elan/EAF_Annotation_Format.pdf)
* Elan Information (http://tla.mpi.nl/tools/tla-tools/elan/elan-description/)
* Elan Tools and Documentation (http://tla.mpi.nl/tools/tla-tools/elan/download/)
* GrAF ISO standards (http://www.iso.org/iso/catalogue_detail.htm?csnumber=37326)

How to use the elan parser
==========================

First is important to know the class DataStructureTypeWithConstraints. This class contains the data structure hierarchy and the dictionary with the constraints.

For the parser works properly is need to set the data structure of the class first:

.. code-block:: python
    # Initialize
    data_hierarchy = ['utterance','words','part_of_speech']

    # Path to the elan file
    inputfile = 'example.elan'

    elan_graf = elan.Elan(inputfile, data.DataStructureTypeWithConstraints())

Next to creat a GrAF object:

.. code-block:: python
    graph = elan_graf.elan_to_graf()

Now it's possible to access it with `Graf-python API <https://github.com/cidles/graf-python>`_

For more information about Graf-python (https://graf-python.readthedocs.org/en/latest/howto.html)

Generate the GrAF files:

.. code-block:: python
    elan_graf.generate_graf_files()

This step will generate the GrAF files inclunding the header and the metafile. Each of the GrAF files is going to be named with the file name of the elan file followed by an extension that is the respective element of the data structure hierarchy. The metafile is named like the GrAF files but the extension will be "extinfo". All the files are xml file type but the header will have a different file extension ".hdr".

Note: To create the GrAF files it's first needed to run the method above described.
