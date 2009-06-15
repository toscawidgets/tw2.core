"""Setuptools setup file"""

import sys, os

from setuptools import setup

if sys.version_info < (2, 5):
    raise SystemExit("Python 2.5 or later is required")

execfile(os.path.join("tw", "release.py"))

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

PACKAGES = [
    'tw2',
    'tw2.core',
    ]

# Requirements to install buffet plugins and engines
_extra_cheetah = ["Cheetah>=1.0", "TurboCheetah>=0.9.5"]
_extra_genshi = ["Genshi >= 0.3.5"]
_extra_kid = ["kid>=0.9.5", "TurboKid>=0.9.9"]
_extra_mako = ["Mako >= 0.1.1"]

setup(
    name=__PACKAGE_NAME__,
    version=__VERSION__,
    description="Web widget creation toolkit based on TurboGears widgets",
    long_description = get_description(),
    install_requires=[
        'WebOb',
        'simplejson >= 2.0',
        ],
    extras_require = {
        'cheetah': _extra_cheetah,
        'kid': _extra_kid,
        'genshi': _extra_genshi,
        'mako': _extra_mako,
        },
    url = "http://toscawidgets.org/",
    download_url = "http://toscawidgets.org/download/",
    author=__AUTHOR__,
    author_email=__EMAIL__,
    license=__LICENSE__,
    packages = PACKAGES,
    namespace_packages = ['tw2'],
    include_package_data=True,
    exclude_package_data={"thirdparty" : ["*"]},
    entry_points="""
    [toscawidgets.widgets]
    tw.core = tw.core

    [turbogears.extensions]
    toscawidgets=tw.core.framework:tg

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


"""
    [paste.filter_app_factory]
    middleware = tw.api:make_middleware
"""
