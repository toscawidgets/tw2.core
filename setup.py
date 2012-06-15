"""Setuptools setup file"""

import sys
import os
import logging

from setuptools import setup

# Ridiculous as it may seem, we need to import multiprocessing and logging here
# in order to get tests to pass smoothly on python 2.7.
try:
    import multiprocessing
    import logging
except:
    pass


def get_description(fname='README.rst'):
    # Adapted from PEAK-Rules' setup.py
    # Get our long description from the documentation
    f = file(fname)
    lines = []
    for line in f:
        if not line.strip():
            break     # skip to first blank line
    for line in f:
        if line.startswith('Documentation contents'):
            break     # read to "Documentation contents..."
        lines.append(line)
    f.close()
    return ''.join(lines)

# Requirements to install buffet plugins and engines
_extra_genshi = ["Genshi >= 0.3.5"]
_extra_mako = ["Mako >= 0.1.1"]
_extra_jinja = ["jinja2"]
_extra_kajiki = ["kajiki"]
_extra_chameleon = ["chameleon"]

requires = [
    'WebOb>=0.9.7',
    'simplejson >= 2.0',
    'PasteDeploy',
    'speaklater',
    'decorator',
    'webhelpers',
]

if sys.version_info[0] == 2 and sys.version_info[1] <= 5:
    requires.append('WebOb<=1.1.1')

setup(
    name='tw2.core',
    version='2.1.0b1',
    description="Web widget creation toolkit based on TurboGears widgets",
    long_description = get_description(),
    install_requires=requires,
    tests_require = [
        'nose',
        'coverage',
        'BeautifulSoup',
        'FormEncode',
        'WebTest',
        'strainer',
    ] + \
    _extra_genshi + \
    _extra_mako + \
    _extra_jinja + \
    _extra_kajiki + \
    _extra_chameleon,

    test_suite = 'nose.collector',
    extras_require = {
        'genshi': _extra_genshi,
        'mako': _extra_mako,
        'jinja': _extra_jinja,
        'kajiki': _extra_kajiki,
        'chameleon': _extra_chameleon,
        },
    url = "http://toscawidgets.org/",
    download_url = "http://toscawidgets.org/download/",
    author='Paul Johnston, Christopher Perkins, Alberto Valverde & contributors',
    author_email='paj@pajhome.org.uk',
    license='MIT',
    packages = ['tw2', 'tw2.core'],
    namespace_packages = ['tw2'],
    include_package_data=True,
    exclude_package_data={"thirdparty" : ["*"]},
    entry_points="""
    [tw2.widgets]
    widgets = tw2.core

    [paste.filter_app_factory]
    middleware = tw2.core.middleware:make_middleware

    [distutils.commands]
    archive_tw2_resources = tw2.core.command:archive_tw2_resources

    """,
    zip_safe=False,
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Environment :: Web Environment :: ToscaWidgets',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
        'Topic :: Software Development :: Widget Sets',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
