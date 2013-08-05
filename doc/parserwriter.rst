Parser and Writer classes to map from and to file formats
*********************************************************

This chapter explains how the Parser and Writer classes in Poio API work. You
will learn how to write your own parsers and writers to support a custom file
format. Poio API already support a lot of file formats out of the box, which
are explained in the following sections. In any case the parser
class is used by a general `Converter` class to map the file format onto
a GrAF object. The user may then modify the GrAF object and write back the
changes to any of the supported file format (or a custom format, if you
implemented a writer). The following Python code demonstrates how one
file format can be convert to another one with support of an existing parser
and writer class:

.. code-block:: python

  parser = poioapi.io.wikipedia_extractor.Parser("Wikipedia.xml")
  writer = poioapi.io.graf.Writer()

  converter = poioapi.io.graf.GrAFConverter(parser, writer)
  converter.parse()
  converter.write("Wikipedia.hdr")

This code parses from the XML output of the `Wikipedia Extractor
<http://medialab.di.unipi.it/wiki/Wikipedia_Extractor>`_ and writes the content
as GrAF files.

**Contents**

.. toctree::
   :maxdepth: 2

   parserwriter_howto
   excel
