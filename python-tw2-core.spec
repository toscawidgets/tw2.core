%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%global modname tw2.core

Name:           python-tw2-core
Version:        2.0.5
Release:        1%{?dist}
Summary:        Web widget creation toolkit based on TurboGears widgets

Group:          Development/Languages
License:        MIT
URL:            http://toscawidgets.org
Source0:        http://pypi.python.org/packages/source/t/%{modname}/%{modname}-%{version}.tar.gz
BuildArch:      noarch

# For building, generally
BuildRequires:  python2-devel
BuildRequires:  python-setuptools
%if %{?rhel}%{!?rhel:0} >= 6
BuildRequires:  python-webob1.0 >= 0.9.7
%else
BuildRequires:  python-webob >= 0.9.7
%endif
BuildRequires:  python-simplejson >= 2.0
BuildRequires:  python-decorator
BuildRequires:  python-speaklater
BuildRequires:  python-paste-deploy

# Specifically for the test suite
BuildRequires:  python-unittest2
BuildRequires:  python-nose
BuildRequires:  python-coverage
BuildRequires:  python-BeautifulSoup
BuildRequires:  python-formencode
BuildRequires:  python-webtest
BuildRequires:  python-strainer

# Templating languages for the test suite
BuildRequires:  python-mako
BuildRequires:  python-genshi
BuildRequires:  python-turbokid
BuildRequires:  python-turbocheetah


# Runtime requirements
%if %{?rhel}%{!?rhel:0} >= 6
Requires:       python-webob1.0 >= 0.9.7
%else
Requires:       python-webob >= 0.9.7
%endif
Requires:       python-simplejson >= 2.0
Requires:       python-decorator
Requires:       python-speaklater
Requires:       python-paste-deploy

%description
ToscaWidgets is a web widget toolkit for Python to aid in the creation,
packaging and distribution of common view elements normally used in the web.

The tw2.core package is lightweight and intended for run-time use only;
development tools are in tw2.devtools.

%prep
%setup -q -n %{modname}-%{version}

%if %{?rhel}%{!?rhel:0} >= 6

# Make sure that epel/rhel picks up the correct version of webob
awk 'NR==1{print "import __main__; __main__.__requires__ = __requires__ = [\"WebOb>=1.0\"]; import pkg_resources"}1' setup.py > setup.py.tmp
mv setup.py.tmp setup.py

# Remove all the fancy nosetests configuration for older python
rm setup.cfg

%endif


%build
%{__python} setup.py build

%install
%{__python} setup.py install -O1 --skip-build \
    --install-data=%{_datadir} --root=%{buildroot}

%check
PYTHONPATH=$(pwd) python setup.py test

%files
%doc README.rst LICENSE.txt
%{python_sitelib}/*

%changelog
* Tue Apr 24 2012 Ralph Bean <rbean@redhat.com> - 2.0.5-1
- Packaged latest version of tw2.core which fixes streaming WSGI compliance.
- Removed defattr in the files section.
- Removed clean section.  Not supporting EPEL5.
- Removed references to buildroot.

* Mon Apr 16 2012 Ralph Bean <rbean@redhat.com> - 2.0.4-1
- Packaged latest version of tw2.core which fixes tests on py2.6.
- Added awk line to make sure pkg_resources picks up the right WebOb on el6
- Added dependency on python-unittest2

* Wed Apr 11 2012 Ralph Bean <rbean@redhat.com> - 2.0.3-1
- Packaged the latest release of tw2.core.
- Fixed rpmlint - python-bytecode-without-source
- Fixed rpmlint - non-executable-script

* Tue Apr 10 2012 Ralph Bean <rbean@redhat.com> - 2.0.2-1
- Packaged the latest release of tw2.core.
- Added the %{?dist} macro to Release:

* Wed Apr 04 2012 Ralph Bean <rbean@redhat.com> - 2.0.1-1
- Update for latest tw2.core release.

* Thu Jun 16 2011 Luke Macken <lmacken@redhat.com> - 2.0-0.1.b4
- Initial package
