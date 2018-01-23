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
BuildRequires: python-setuptools
Requires: python python2-django >= 1.10 python-idna fred-idl fred-pyfco uwsgi-plugin-python httpd mod_proxy_uwsgi

%description
RDAP server for FRED registry system

%prep
%setup -n %{name}-%{unmangled_version}

%install
python setup.py install -cO2 --force --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES --prefix=/usr

mkdir -p $RPM_BUILD_ROOT/etc/httpd/conf.d/
install contrib/fedora/apache.conf $RPM_BUILD_ROOT/etc/httpd/conf.d/fred-rdap-apache.conf

mkdir -p $RPM_BUILD_ROOT/etc/uwsgi.d/
install contrib/fedora/uwsgi.ini $RPM_BUILD_ROOT/etc/uwsgi.d/rdap.ini

mkdir -p $RPM_BUILD_ROOT/etc/fred/
install contrib/fedora//rdap_cfg.py $RPM_BUILD_ROOT/etc/fred/

%clean
rm -rf $RPM_BUILD_ROOT

%post
test -f /var/log/fred-rdap.log || touch /var/log/fred-rdap.log; chown uwsgi.uwsgi /var/log/fred-rdap.log; chcon -t httpd_log_t /var/log/fred-rdap.log

chcon -Rt httpd_sys_content_rw_t /run/uwsgi/

%files -f INSTALLED_FILES
%defattr(-,root,root)
/etc/httpd/conf.d/fred-rdap-apache.conf
/etc/fred/rdap_cfg.py
%attr(-,uwsgi,uwsgi) /etc/uwsgi.d/rdap.ini
