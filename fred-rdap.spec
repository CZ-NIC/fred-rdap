%define name fred-rdap
%define release 1
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%define debug_package %{nil}

Summary: CZ.NIC RDAP
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: GNU GPL
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: CZ.NIC <fred@nic.cz>
Url: https://fred.nic.cz/
BuildRequires: fred-distutils
Requires: python python-django fred-idl python-omniORB httpd mod_wsgi python-idna

%description
CZ.NIC RDAP server

%prep
%setup -n %{name}-%{unmangled_version}

%build
python setup.py build


%install
python setup.py install -cO2 --force --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES --prefix=/usr --install-sysconf=/etc --install-localstate=/var --wsgirundir=/var/run/ --rdappath="/rdap"


%clean
rm -rf $RPM_BUILD_ROOT

%post
test -f /etc/httpd/conf.d/fred-rdap-apache.conf || ln -s /usr/share/fred-rdap/apache.conf /etc/httpd/conf.d/fred-rdap-apache.conf
test -f /var/log/fred-rdap.log || touch /var/log/fred-rdap.log; chown apache.apache /var/log/fred-rdap.log; chcon -t httpd_log_t /var/log/fred-rdap.log


%preun
test ! -f /etc/httpd/conf.d/fred-rdap-apache.conf || rm /etc/httpd/conf.d/fred-rdap-apache.conf


%files -f INSTALLED_FILES
%defattr(-,root,root)
