from distutils.core import setup
import py2exe

setup(
    name = 'ebookutils',
    version = open('..\VERSION').read().strip(),
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
    packages   = ['impserve'],
    console    = ['run.py'],
    options    = { "py2exe": {
                                "unbuffered": True,
                                "optimize": 2,
                                "includes": ['BeautifulSoup']
                             } }
)
