*********************************
How to convert GrAF files to brat
*********************************

First brat is a web-based tool for text annotation (http://brat.nlplab.org/).
It works quite simple, through a annotation file with a **same name** of a text file, using the tokens in it, parses the
text file in order to find the annotations using the token ranges.
The annotations configuration are specified in a file name "annotation.conf", this file is also required otherwise the
brat will through warnings and errors about the annotations.

Our convert will be based in the data from QuantHistLing project (http://www.quanthistling.info/data). The annotation
file should be like this:

.. code-block:: xml

    [entities]
    formatting
        italic
        tab
        newline
        bold
        underline
        superscript
        smallcaps
        hyphen
        pagebreak
    dictinterpretation
        head
        pos
        translation
        crossreference
        counterpart
        footnote
        stratum
        phonology
        boundary
        dialectidentification
        headorth
        typo
        iso-639-3
            spa
            des
        doculect
            Desano
            Espan_ol

    [relations]
    # To Arg1:<ENTITY>, Arg2:<ENTITY>
    <OVERLAP>	Arg1:<ENTITY>, Arg2:<ENTITY>, <OVL-TYPE>:<ANY>

    [events]
    # none

    [attributes]
    # none

For this demonstration we will use the GrAF files from the Aleman2000 dictionary.

To convert a GrAF file to brat first is need to have a GrAF object:

.. code-block:: python

    parser = graf.io.GraphParser()
    graf_graph = parser.parse("dict-aleman2000-9-69.hdr")

Once we get the graph object is need to set the brat writer.
The brat writer is defined with two paremeters: annotation_space and feature_name.

* The annotation_space serves to filter what annotations are wanted from the graph object to write in brat annotation file.
* The feature_name é a feature key that contains the real value of each annotation.

.. code-block:: python

    brat = poioapi.io.brat.Writer("dictinterpretation", feature_name="substring")

In our case we want go get only the annotations from "dictinterpretation" and that contain the feature "substring":

.. code-block:: python

    brat.write(outputfilename="dict-aleman2000-9-69.ann", graf_graph)

The result should be a file named "dict-aleman2000-9-69.ann".

.. code-block:: python

    T1	head 0 6	áriri
    #1	AnnotatorNotes T1	NodeID = aleman2000/9/7/annotation/2
    T2	Desano 0 6	áriri
    #2	AnnotatorNotes T2	NodeID = aleman2000/9/7/annotation/2
    T3	des 0 6	áriri
    [...]

**Note:** In order to brat works properly the result file (filename.ann) should have the same name as the text file.