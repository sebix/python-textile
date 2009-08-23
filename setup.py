#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup

setup(name='textile',
      version='2.1.3',
      description='This is Textile. A Humane Web Text Generator.',
      author='Jason Samsa',
      author_email='jsamsa@gmail.com',
      url='http://loopcore.com/python-textile/',
      py_modules=['textile'],
      platforms = ['any'],
      license = ['BSD'],
      long_description = """
        Textile is a XHTML generator using a simple markup developed by Dean Allen.
        Python 2.4 users will need to install the uuid module
        """,

      setup_requires=['nose>=0.11', 'coverage>=3.0.1'],
      test_suite = 'nose.collector',
      tests_require = ['nose']
      )
