"""Setuptools setup file"""

from setuptools import setup, find_packages

# Requirements to install buffet plugins and engines
_extra_cheetah = ["Cheetah>=1.0", "TurboCheetah>=0.9.5"]
_extra_genshi = ["Genshi >= 0.3.5"]
_extra_kid = ["kid>=0.9.5", "TurboKid>=0.9.9"]
_extra_mako = ["Mako >= 0.1.1"]

setup(
    name='tw2.core',
    version='2.0b4',
    description="Web widget creation toolkit based on TurboGears widgets",
    long_description = open('README.txt').read().split('\n\n', 1)[1],
    install_requires=[
        'WebOb>=0.9.7',
        'simplejson >= 2.0',
        'decorator',
        ],
    tests_require = ['nose', 'BeautifulSoup', 'FormEncode', 'WebTest', 'strainer'] + _extra_cheetah + _extra_genshi + _extra_kid + _extra_mako,
    test_suite = 'nose.collector',
    extras_require = {
        'cheetah': _extra_cheetah,
        'kid': _extra_kid,
        'genshi': _extra_genshi,
        'mako': _extra_mako,
        },
    url = "http://toscawidgets.org/documentation/tw2.core/",
    author='Paul Johnston, Christopher Perkins, Alberto Valverde & contributors',
    author_email='paj@pajhome.org.uk',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'tests']),
    namespace_packages = ['tw2'],
    include_package_data=True,
    exclude_package_data={"thirdparty" : ["*"]},
    entry_points="""
    [tw2.widgets]
    tw2.core = tw2.core

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
