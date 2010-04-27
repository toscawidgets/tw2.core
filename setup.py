"""Setuptools setup file"""

import sys, os

from setuptools import setup

def get_description(fname='README.txt'):
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
_extra_cheetah = ["Cheetah>=1.0", "TurboCheetah>=0.9.5"]
_extra_genshi = ["Genshi >= 0.3.5"]
_extra_kid = ["kid>=0.9.5", "TurboKid>=0.9.9"]
_extra_mako = ["Mako >= 0.1.1"]

setup(
    name='tw2.core',
    version='2.0b3',
    description="Web widget creation toolkit based on TurboGears widgets",
    long_description = get_description(),
    install_requires=[
        'WebOb>=0.9.7',
        'simplejson >= 2.0',
        'decorator',
        ],
    tests_require = ['nose', 'BeautifulSoup', 'FormEncode', 'WebTest', 'strainer'],
    test_suite = 'nose.collector',
    extras_require = {
        'cheetah': _extra_cheetah,
        'kid': _extra_kid,
        'genshi': _extra_genshi,
        'mako': _extra_mako,
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
    tw2.core = tw2.core

    [turbogears.extensions]
    toscawidgets=tw.core.framework:tg

    [paste.filter_app_factory]
    middleware = tw2.core.middleware:make_middleware

    """,
    zip_safe=False,
    classifiers = [
        'Development Status :: 3 - Alpha',
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
