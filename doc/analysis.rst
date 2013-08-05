Linguistic analysis and pipelines based on GrAF graphs
======================================================

We think that GrAF graphs can play an important role in the implementation
of scientific workflows in linguistics. Based on the GrAF objects that
Poio API generates you might pipe the data to scientific Python libraries
like `networkx <http://networkx.github.io/>`_, `numpy <http://www.numpy.org/>`_
or `scipy <http://www.scipy.org/>`_. The American National Corpus implemented
connectors for GrAF and two linguistic frameworks. The conversion of custom
file formats to GrAF through Poio API can thus act as an entry point to those
pipelines and support to merge data and annotation from a wide range of
heteregenous data sources for further analysis.


Counting word orders
--------------------

The following example is based on the parser explained in section
:ref:`excel_parser`. The whole workflow to count word order in GrAF is
implemented as `IPython notebook <http://ipython.org/notebook.html>`_, which
you can view and download here:

http://nbviewer.ipython.org/urls/raw.github.com/pbouda/notebooks/master/Diana%20Hinuq%20Word%20Order.ipynb


D3.js for visualization
-----------------------

The graf-python documentation contains a nice example how to visualize GrAF
data with the help of the `networkx library <http://networkx.github.io/>`_
and the Javascript visualization library `D3.js <http://d3js.org/>`_:

https://graf-python.readthedocs.org/en/latest/Translation%20Graph%20from%20GrAF.html

To just see the example visualization click here:

http://bl.ocks.org/anonymous/4250342


GrAF connectors
---------------

The American National Corpus implemented GrAF connectors for the `Unstructured
Information Management applications (Apache UIMA) <http://uima.apache.org/>`_
fraemwork and the `general architecture for text engineering (GATE)
<http://gate.ac.uk/>`_ software. You can download the ANC software here:

http://www.anc.org/software/uimautils/
http://www.anc.org/software/gate-tools/
