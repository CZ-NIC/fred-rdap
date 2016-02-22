#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

from freddist.command.install import install
from freddist.core import setup
from freddist.util import findall, find_data_files, find_packages


PROJECT_NAME = 'fred-rdap'


class ModuleInstall(install):

    user_options = install.user_options + [
        ('host=', None,
         'RDAP host'),
        ('port=', None,
         'RDAP port'),
        ('rdappath=', None,
         'RDAP path'),
        ('unixwhoishost=', None,
         'host of related unix whois protocol'),
        ('nshostport=', None,
         'host:port of CORBA name service'),
        ('wsgirundir=', None,
         'Directory for WSGI socket'),
        ('disclaimerfile=', None,
         'File with disclaimer')
    ]

    def initialize_options(self):
        install.initialize_options(self)
        self.host = "localhost"
        self.port = None
        self.unixwhoishost = None
        self.nshostport = None
        self.wsgirundir = ""
        self.disclaimerfile = None
        self.rdappath = "/rdap"

    def update_rdap_cfg_py(self, filename):
        content = open(filename).read()
        content = content.replace("CORBA_IDL_ROOT_PATH = ''", "CORBA_IDL_ROOT_PATH = '" + self.expand_filename('$data/share/idl/fred') + "'")
        if self.nshostport is not None:
            content = content.replace("CORBA_NS_HOST_PORT = ''", "CORBA_NS_HOST_PORT = '" + self.nshostport + "'")
        hostport = self.host
        if self.port is not None:
            hostport = hostport + ":" + self.port
        content = content.replace("RDAP_ROOT_URL = ''", "RDAP_ROOT_URL = 'http://" + hostport + self.rdappath + "'")
        if self.unixwhoishost is not None:
            content = content.replace("UNIX_WHOIS_HOST = ''", "UNIX_WHOIS_HOST = '" + self.unixwhoishost + "'")
        if self.disclaimerfile is not None:
            content = content.replace("DISCLAIMER_FILE = ''", "DISCLAIMER_FILE = '" + self.disclaimerfile + "'")

        open(filename, 'w').write(content)
        self.announce("File '%s' was updated" % filename)

    def update_apache_conf(self, filename):
        content = open(filename).read()
        content = content.replace("INSTALL_PURELIB", self.expand_filename('$purelib/rdap'))
        content = content.replace("WSGI_FILE", self.expand_filename('$purelib/rdap/run.wsgi'))
        content = content.replace("RDAP_PATH", self.rdappath)
        if self.port is not None:
            content = "Listen " + self.port + "\n" + content
        content = content.replace("WSGI_RUN_DIR_ROOT", self.wsgirundir)

        open(filename, 'w').write(content)
        self.announce("File '%s' was updated" % filename)

    def update_run_wsgi(self, filename):
        content = open(filename).read()
        content = content.replace("PURELIB_DIR", self.expand_filename('$purelib'))
        content = content.replace("PURELIB_RDAP_DIR", self.expand_filename('$purelib/rdap'))
        content = content.replace("SYSCONF_DIR", self.expand_filename('$sysconf/fred'))

        open(filename, 'w').write(content)
        self.announce("File '%s' was updated" % filename)


def main():
    setup(name=PROJECT_NAME,
          description='NIC.CZ RDAP',
          author='Jan Korous, CZ.NIC',
          author_email='jan.korous@nic.cz',
          url='http://www.nic.cz/',
          license='GNU GPL',
          platforms=['posix'],
          long_description='CZ.NIC RDAP server',
          packages=('rdap', 'rdap.rdap_rest', 'rdap.utils'),
          package_data={
              'rdap': ['rdap/*'],
              'rdap.utils': ['rdap/utils/*'],
              'rdap.rdap_rest': ['rdap/rdap_rest/*'],
          },
          data_files=[
              ('$sysconf/fred/', ['settings_rdap/rdap_cfg.py']),
              ('$data/share/fred-rdap', ['settings_rdap/apache.conf']),
              ('$sysconf/fred/', ['settings_rdap/rdap_disclaimer.txt']),
              ('$purelib/rdap', ['rdap/run.wsgi'])
          ],
          cmdclass={'install': ModuleInstall},
          modify_files={
              '$sysconf/fred/rdap_cfg.py': 'update_rdap_cfg_py',
              '$data/share/fred-rdap/apache.conf': 'update_apache_conf',
              '$purelib/rdap/run.wsgi': 'update_run_wsgi'
          }
    )


if __name__ == '__main__':
    main()
