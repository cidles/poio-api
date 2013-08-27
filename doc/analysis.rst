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


Search in annotation graphs: Filters and filter chains
------------------------------------------------------

The **filter** class :py:class:`poioapi.annotationgraph.AnnotationGraphFilter`
can be used to search in annotation graphs in Poio API. The filter class can
only be used together with the annotation graph class
:py:class:`poioapi.annotationgraph.AnnotationGraph`. The idea is that
each annotation graph can contain a set of filters, that each reduce the
full annotation graph to a subset. This list of filters is what we call a
**filter chain**. Each filter consists of search terms for each of the
tiers that were loaded from an input file, as described in section
:ref:`data_structure_types`. The search terms can be simple strings or
regular expressions.

To be able to apply a filter to an annotation graph you have to load some
data first. In this example we will use the `example file from the Elan
homepage <http://tla.mpi.nl/tools/tla-tools/elan/download/>`_. First, we
create a new annotation graph and load the file:

.. code-block:: python

    import poioapi.annotationgraph

    ag = poioapi.annotationgraph.AnnotationGraph()
    ag.from_elan("elan-example3.eaf")

In the next step we set the default tier hierarchy for the annotation graph.
As the example file contains four root tiers with subtiers we have to choose
one of the hierarchies carefully. In our case we choose the hierarchy with
the root tier `utterance..W-Spch` that we find at index `1` of the
property `ag.tier_hierarchies` after we loaded the file. We choose this
tier hierchary to be used for all subsequent filter operations:

.. code-block:: python

    ag.structure_type_handler = \
        poioapi.data.DataStructureType(ag.tier_hierarchies[1])

In our case the hierarchy `ag.tier_hierarchies[1]` contains the following
tiers:

.. code-block:: python

    ['utterance..W-Spch',
        ['words..W-Words',
            ['part_of_speech..W-POS']],
        ['phonetic_transcription..W-IPA']]

Now we are ready to create a filter for the data. We will filter the data
with serch terms on two of the subtiers of our tier hierarchy: we will search
for ``follow`` on the `words` tier and for the regular expression ``\bpro\b``
on the `POS` tier. We can look up the full names of the tiers in the above
tier hierarchy. The following code creates a filter object and adds the
two search terms for the two tiers:

.. code-block:: python

    af = poioapi.annotationgraph.AnnotationGraphFilter(ag)
    af.set_filter_for_tier("words..W-Words", "follow")
    af.set_filter_for_tier("part_of_speech..W-POS", r"\bpro\b")

The final step is to append the filter to the filter chain of the annotation
graph:

.. code-block:: python

    ag.append_filter(af)

The append operation will already start the process of graph filtering. The
result is stored in the property `filtered_node_ids` of the annotation
graph object, which is a list of root nodes where child nodes matched
the search term:

.. code-block:: python

    print(ag.filtered_node_ids)
    [['utterance..W-Spch..na10',
      'utterance..W-Spch..na12',
      'utterance..W-Spch..na19']]

You can get a visible result set by writing a filtered HTML representation
of the annotation graph:

.. code-block:: python

    import codecs
    html = ag.as_html_table(True)
    f = codecs.open("test.html", "w", "utf-8")
    f.write(html)
    f.close()

You can add more filters to the annotation graph by creating more filter
object and passing them to `append_filter()`. If you want to remove a filter
you can call `pop_filter()`, which will remove the filter that was last added
to the annotation graph object:

.. code-block:: python

    ag.pop_filter()

A convenient way to create filter objects is by passing a dictionary with
tier names and search terms to the method `create_filter_for_dict()` of the
annotation graph object. The following code will create the same filter as
our example above:

.. code-block:: python

    search_terms = {
        "words..W-Words": "follow",
        "part_of_speech..W-POS": r"\bpro\b"
    }
    af = ag.create_filter_for_dict(search_terms)

You can then append the filter to the filter chain. A complete script that
demonstrates filters and filter chains is available on Github:

https://github.com/cidles/poio-api/blob/master/examples/filter.py


Real world examples
-------------------

Counting word orders
....................

The following example is based on the parser explained in section
:ref:`excel_parser`. The whole workflow to count word order in GrAF is
implemented as `IPython notebook <http://ipython.org/notebook.html>`_, which
you can view and download here:

http://nbviewer.ipython.org/urls/raw.github.com/pbouda/notebooks/master/Diana%20Hinuq%20Word%20Order.ipynb


D3.js for visualization
.......................

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

* http://www.anc.org/software/uimautils/
* http://www.anc.org/software/gate-tools/
