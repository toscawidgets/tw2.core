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
    f = open(fname, 'r')
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
_extra_chameleon = ["chameleon"]

requires = [
    'WebOb>=0.9.7',
    'PasteDeploy',
    'speaklater',
    'decorator',
    'markupsafe',
    'six',
]

if sys.version_info[0] == 2 and sys.version_info[1] <= 5:
    requires.append('WebOb<=1.1.1')

tests_require = [
    'nose',
    'sieve',
] + \
    _extra_genshi + \
    _extra_mako + \
    _extra_jinja + \
    _extra_chameleon

if sys.version_info[0] == 2:
    # Broken for py3
    tests_require.append("Formencode")

if sys.version_info[0] == 2 and sys.version_info[1] <= 5:
    tests_require.append('WebTest<2.0.0')
else:
    tests_require.append('WebTest')


setup(
    name='tw2.core',
    version='2.2.1.1',
    description='The runtime components for ToscaWidgets 2, a web widget toolkit.',
    long_description=get_description(),
    author='Paul Johnston, Christopher Perkins, Alberto Valverde Gonzalez & contributors',
    author_email='toscawidgets-discuss@googlegroups.com',
    url="http://toscawidgets.org/",
    download_url="https://pypi.python.org/pypi/tw2.core/",
    license='MIT',
    install_requires=requires,
    tests_require=tests_require,
    test_suite='nose.collector',
    extras_require={
        'genshi': _extra_genshi,
        'mako': _extra_mako,
        'jinja': _extra_jinja,
        'chameleon': _extra_chameleon,
        },
    packages=['tw2', 'tw2.core'],
    namespace_packages=['tw2'],
    include_package_data=True,
    exclude_package_data={"thirdparty": ["*"]},
    entry_points="""
    [tw2.widgets]
    widgets = tw2.core

    [paste.app_factory]
    dev_server = tw2.core.middleware:make_app

    [paste.filter_app_factory]
    middleware = tw2.core.middleware:make_middleware
    """ +  """ # Is this broken for py3?
    [distutils.commands]
    archive_tw2_resources = tw2.core.command:archive_tw2_resources
    """ if sys.version_info[0] == 2 else "",
    zip_safe=False,
    classifiers=[
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
