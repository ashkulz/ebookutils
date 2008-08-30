#!/usr/bin/env python
from __future__ import with_statement

version = open('VERSION').read().strip()

with open('impmake/src/version.h', 'w') as f:
    f.write('#define VERSION "%s"\n' % version)

with open('impserve/impserve/version.py', 'w') as f:
    f.write('__version__ = "%s"\n' % version)
