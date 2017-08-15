#!/usr/bin/python
# -*- coding: utf-8 -*-
from freddist.core import setup


PROJECT_NAME = 'fred-rdap'


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
          })


if __name__ == '__main__':
    main()
