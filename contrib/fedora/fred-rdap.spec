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
%if 0%{?centos}
BuildRequires: policycoreutils-python
%else
BuildRequires: policycoreutils-python-utils
%endif


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

install -d $RPM_BUILD_ROOT/var/run/rdap/

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [[ $1 -eq 1 ]]
then

export rdap_log_file=/var/log/fred-rdap.log
[[ -f $rdap_log_file ]] || install -o uwsgi -g uwsgi /dev/null $rdap_log_file
semanage fcontext -a -t httpd_log_t $rdap_log_file
restorecon $rdap_log_file

export rdap_socket_dir=/var/run/rdap
[[ -f $rdap_socket_dir ]] || install -o uwsgi -g uwsgi -d $rdap_socket_dir
semanage fcontext -a -t httpd_sys_rw_content_t "$rdap_socket_dir(/.*)?"
restorecon -R $rdap_socket_dir

# This is necessary because sometimes SIGPIPE is being blocked when the scriptlet
# executes and reading from /dev/urandom never ends even though the process on the
# other end of the pipe has been long dead.
create_random_string_made_of_50_characters()
{
    local ret=''
    for ((;;))
        do
            local str=$(head -c512 </dev/urandom | tr -cd '[:alnum:]')
            [[ -n $str ]] && ret=${ret}${str}
            [[ ${#ret} -ge 50 ]] && break
        done
    printf "%s" ${ret:0:50}
}

# Fill SECRET_KEY and ALLOWED_HOSTS
sed -i "s/SECRET_KEY = .*/SECRET_KEY = '$(create_random_string_made_of_50_characters)'/g" %{_sysconfdir}/fred/rdap_cfg.py
sed -i "s/ALLOWED_HOSTS = \[\]/ALLOWED_HOSTS = \['localhost', '$(hostname)'\]/g" %{_sysconfdir}/fred/rdap_cfg.py

fi
exit 0

%postun
if [[ $1 -eq 0 ]]
then
    semanage fcontext -d -t httpd_log_t /var/log/fred-rdap.log
    semanage fcontext -d -t httpd_sys_rw_content_t "/var/run/rdap(/.*)?"
fi
exit 0

%files -f INSTALLED_FILES
%defattr(-,root,root)
%config %{_sysconfdir}/httpd/conf.d/fred-rdap-apache.conf
%config %{_sysconfdir}/fred/rdap_cfg.py
%config %attr(-,uwsgi,uwsgi) %{_sysconfdir}/uwsgi.d/rdap.ini
%ghost %attr(-,uwsgi,uwsgi) /var/run/rdap/
