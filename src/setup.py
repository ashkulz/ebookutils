extra_opts = {}
try:
    from setuptools import setup
    extra_opts.update({ 'entry_points' : {
        'console_scripts': [
            'impserve = ebookutils.impserve:main',
        ]
    }})
except ImportError:
    from distutils.core import setup

try:
    import sys, py2exe
    sys.path.append('plugins')
    extra_opts.update({
        'console': ['impserve.py'],
        'options': { "py2exe": {
            "unbuffered": True,
            "optimize": 2,
            "includes": ['BeautifulSoup', 'subprocess']
        } }
    })
except ImportError:
    pass

setup(
    name = 'ebookutils',
    version = open('../VERSION').read().strip(),
    author = 'Ashish Kulkarni',
    author_email = 'kulkarni.ashish@gmail.com',
    description = 'This is a collection of utilities which are useful for working with ebooks.',
    license = 'zlib/libpng',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
    packages   = ['ebookutils'],
    **extra_opts
)
