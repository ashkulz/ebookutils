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
    description = 'ebookutils is a collection of utilities which are useful for working with ebooks.',
    long_description = open('../README').read().strip(),
    license = 'zlib/libpng',
    url = 'http://ebookutils.berlios.de/',
    download_url = 'http://ebookutils.berlios.de/',
    scripts = ['impbuild.exe'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: zlib/libpng License',
        'Operating System :: OS Independent',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows :: Windows NT/2000',
        'Programming Language :: Python',
        'Programming Language :: C',
        'Topic :: Desktop Environment',
        'Topic :: Utilities',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers'
    ],
    packages   = ['ebookutils'],
    **extra_opts
)
