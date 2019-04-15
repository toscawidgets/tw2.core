ToscaWidgets
============

ToscaWidgets is a web widget toolkit for Python to aid in the creation,
packaging and distribution of common view elements normally used in the web::

  import tw2.core as twc

  class HelloWidget(twc.Widget):
      inline_engine_name = "kajiki"
      template = """
          <i>Hello ${w.name}</i>
      """

      name = twc.Param(description="Name of the greeted entity")

  >>> HelloWidget(name="World").display()
  <i>Hello World</i>

The tw2.core package is lightweight and provides the runtime of
ToscaWidgets, all machinery related to forms is provided by tw2.forms::

    import tw2.core as twc
    import tw2.forms as twf

    class MovieForm(twf.Form):
        class child(twf.TableLayout):
            title = twf.TextField()
            director = twf.TextField(value='Default Director')
            genres = twf.SingleSelectField(options=['Action', 'Comedy', 'Romance', 'Sci-fi'])

        action = '/save_movie'

Build Status
------------

.. |travis-master| image:: https://secure.travis-ci.org/toscawidgets/tw2.core.png?branch=master
   :alt: Build Status - master branch
   :target: http://travis-ci.org/#!/toscawidgets/tw2.core

.. |travis-develop| image:: https://secure.travis-ci.org/toscawidgets/tw2.core.png?branch=develop
   :alt: Build Status - develop branch
   :target: http://travis-ci.org/#!/toscawidgets/tw2.core

.. |coveralls-master| image:: https://coveralls.io/repos/toscawidgets/tw2.core/badge.svg?branch=master&service=github
   :alt: Test Coverage - master branch
   :target: https://coveralls.io/github/toscawidgets/tw2.core?branch=master

.. |coveralls-develop| image:: https://coveralls.io/repos/toscawidgets/tw2.core/badge.svg?branch=develop&service=github
   :alt: Test Coverage - develop branch
   :target: https://coveralls.io/github/toscawidgets/tw2.core?branch=develop

+--------------+------------------+---------------------+
| Branch       | Build Status     | Test Coverage       |
+==============+==================+=====================+
| **master**   | |travis-master|  | |coveralls-master|  |
+--------------+------------------+---------------------+
| **develop**  | |travis-develop| | |coveralls-develop| |
+--------------+------------------+---------------------+

Documentation
-------------

Documentation is hosted at `ReadTheDocs <http://tw2core.rtfd.org>`_.
