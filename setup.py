from distutils.core import setup
setup(name='poioapi',
      version='0.3.0',
      description='Python Linguistic Annotation Library',
      long_description='PoioAPI is a Python Library to access and manipulate linguistically annotated corpus files. Supported file format is currently Elan XML, Kura XML and Toolbox files. A Corpus Reader API is provided to support statistical analysis within the Natural Language Toolkit. ',
      author='Peter Bouda',
      author_email='pbouda@cidles.eu',
      url='http://ltll.cidles.eu/poio/poio-api/',
      packages=[ 'poioapi', 'poioapi.tests' ],
      package_dir={'poioapi': 'src/poioapi'},
      package_data={'poioapi': ['xsl/*.xsl', 'xsd/*.xsd']},
      )
