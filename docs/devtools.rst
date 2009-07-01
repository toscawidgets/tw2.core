tw2.devtools Design
-------------------

To keep tw2.core as minimal as possible, features needed only for development are in a separate package, tw2.devtools. The features in devtools are:

 * Documentation
 * Widget browser
 * Widget library quick start
 * Unit tests


Widget Browser
==============




The parameters that are displayed are: all the required parameters, plus non-required parameters that are defined on anything other than the Widget base class. Variables are never shown.


Widget Library Quick Start
==========================



Unit Tests
==========

To run the tests, in ``tw2.devtools/tests`` issue::

    nosetests --with-doctest --doctest-extension=.txt
