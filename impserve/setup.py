#!/usr/bin/env python

from distutils.core import setup
from version import __version__

setup(name='impserve',
      version=__version__,
      description='content server and internet proxy for the REB 1150/1200 ebooks',
      py_modules = ['version'],
      scripts = ['impserve.py']
     )
