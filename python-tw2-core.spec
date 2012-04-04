%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%global prerel b6
%global modname tw2.core

Name:           python-tw2
Version:        2.0
Release:        0.1.%{prerel}%{?dist}
Summary:        Web widget creation toolkit based on TurboGears widgets

Group:          Development/Languages
License:        MIT
URL:            http://toscawidgets.org
Source0:        http://pypi.python.org/packages/source/t/%{modname}/%{modname}-%{version}%{prerel}.tar.gz
Patch0:         tw2-test_genshi_abs.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch

BuildRequires:  python2-devel
BuildRequires:  python-setuptools

Requires:       python-webob >= 0.9.7
Requires:       python-simplejson >= 2.0
Requires:       python-decorator

%description
ToscaWidgets is a web widget toolkit for Python to aid in the creation,
packaging and distribution of common view elements normally used in the web.

The tw2.core package is lightweight and intended for run-time use only;
development tools are in tw2.devtools.

%prep
%setup -q -n %{modname}-%{version}%{prerel}
%patch0

%build
%{__python} setup.py build

%install
rm -rf %{buildroot}
%{__python} setup.py install -O1 --skip-build \
    --install-data=%{_datadir} --root %{buildroot}

%check
PYTHONPATH=$(pwd) python setup.py test

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc README.txt LICENSE.txt CHANGELOG.txt
%{python_sitelib}/*

%changelog
* Thu Jun 16 2011 Luke Macken <lmacken@redhat.com> - 2.0-0.1.b4
- Initial package
