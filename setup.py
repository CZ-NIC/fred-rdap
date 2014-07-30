#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

from freddist.command.install import install
from freddist.core import setup
from freddist.util import findall, find_data_files, find_packages


PROJECT_NAME = 'rdap'


class ModuleInstall(install):
    
    user_options = install.user_options + [
        ('host=', None,
         'RDAP host'),
        ('port=', None,
         'RDAP port'),
        ('unixwhoishost=', None,
         'host of related unix whois protocol'),
        ('nshostport=', None,
         'host:port of CORBA name service'),
        ('wsgirundir=', None,
         'Directory for WSGI socket')
    ]
    
    def initialize_options(self):
        install.initialize_options(self)
        self.host = None
        self.port = None
        self.unixwhoishost = None
        self.nshostport = None
        self.wsgirundir = None

    def update_rdap_cfg_py(self, filename):
        if self.nshostport is not None or self.host is not None or self.unixwhoishost is not None:
            content = open(filename).read()
            content = content.replace("CORBA_IDL_ROOT_PATH = ''",       "CORBA_IDL_ROOT_PATH = '" + self.expand_filename('$data/share/idl/fred') + "'")
            content = content.replace("CORBA_NS_HOST_PORT = ''",        "CORBA_NS_HOST_PORT = '" + self.nshostport + "'")
            content = content.replace("RDAP_ROOT_URL = ''",             "RDAP_ROOT_URL = 'http://" + self.host + ":" + self.port + "'")
            content = content.replace("UNIX_WHOIS_HOST = ''",           "UNIX_WHOIS_HOST = '" + self.unixwhoishost + "'")

            open(filename, 'w').write(content)
            self.announce("File '%s' was updated" % filename)
        
    def update_apache_conf(self, filename):
        if self.port is not None or self.wsgirundir is not None:
            content = open(filename).read()
            content = content.replace("INSTALL_PURELIB", self.expand_filename('$purelib/rdap'))
            content = content.replace("LISTEN_PORT", self.port)
            content = content.replace("WSGI_RUN_DIR_ROOT", self.wsgirundir)

            open(filename, 'w').write(content)
            self.announce("File '%s' was updated" % filename)
        
    def update_run_wsgi(self, filename):
        if self.wsgirundir is not None:
            content = open(filename).read()
            content = content.replace("ROOT_DIR", self.expand_filename('$data'))

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
              ('$data/share/rdap', ['settings_rdap/apache.conf']),
              ('$purelib/rdap', ['rdap/run.wsgi'])
          ],
          cmdclass={'install': ModuleInstall},
          modify_files={
              '$sysconf/fred/rdap_cfg.py': 'update_rdap_cfg_py',
              '$data/share/rdap/apache.conf': 'update_apache_conf',
              '$purelib/rdap/run.wsgi': 'update_run_wsgi'
          }
    )


if __name__ == '__main__':
    main()
