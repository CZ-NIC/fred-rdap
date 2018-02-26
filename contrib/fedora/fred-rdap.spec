%define name fred-rdap
%define release 1
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%define debug_package %{nil}

Summary: RDAP server for FRED registry system
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

mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/httpd/conf.d/
install contrib/fedora/apache.conf $RPM_BUILD_ROOT/%{_sysconfdir}/httpd/conf.d/fred-rdap-apache.conf

mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/uwsgi.d/
install contrib/fedora/uwsgi.ini $RPM_BUILD_ROOT/%{_sysconfdir}/uwsgi.d/rdap.ini

mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/fred/
install contrib/fedora/rdap_cfg.py $RPM_BUILD_ROOT/%{_sysconfdir}/fred/

%clean
rm -rf $RPM_BUILD_ROOT

%post
# Allow to write to config file in SELINUX environment
test -f /var/log/fred-rdap.log || touch /var/log/fred-rdap.log;
chown uwsgi.uwsgi /var/log/fred-rdap.log;
chcon -t httpd_log_t /var/log/fred-rdap.log
# Allow to write to uwsgi socket in SELINUX environment
test -d /run/uwsgi || install -o uwsgi -g uwsgi -d /run/uwsgi/
chcon -Rt httpd_sys_content_rw_t /run/uwsgi/
# Generate SECRET_KEY
KEY=$(tr -cd '[:alnum:]' < /dev/urandom | fold -w50 | head -n1)
sed -i "s/SECRET_KEY = .*/SECRET_KEY = '$KEY'/g" %{_sysconfdir}/fred/rdap_cfg.py
# Fill ALLOWED_HOSTS
sed -i "s/ALLOWED_HOSTS = \[\]/ALLOWED_HOSTS = \['localhost', '$(hostname)'\]/g" %{_sysconfdir}/fred/rdap_cfg.py

%files -f INSTALLED_FILES
%defattr(-,root,root)
%{_sysconfdir}/httpd/conf.d/fred-rdap-apache.conf
%{_sysconfdir}/fred/rdap_cfg.py
%attr(-,uwsgi,uwsgi) %{_sysconfdir}/uwsgi.d/rdap.ini
