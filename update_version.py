#!/usr/bin/env python
import os, sys

os.chdir(os.path.join(os.path.dirname(sys.argv[0])))
version = open('VERSION').read().strip()
if '-dev' in sys.argv:
    version += '-dev'

open('impmake/src/version.h', 'w').write('#define VERSION "%s"\n' % version)
open('impserve/impserve/version.py', 'w').write('__version__ = "%s"\n' % version)
