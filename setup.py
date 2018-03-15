#!/usr/bin/python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup


setup(name='fred-rdap',
      description='NIC.CZ RDAP',
      version='0.11.0',
      author='Jan Korous, CZ.NIC',
      author_email='jan.korous@nic.cz',
      url='http://www.nic.cz/',
      license='GNU GPL',
      platforms=['posix'],
      long_description='CZ.NIC RDAP server',
      packages=find_packages(),
      include_package_data=True,
      install_requires=open('requirements.txt').read().splitlines(),
      extras_require={'testing': ['mock'],
                      'quality': ['isort', 'flake8', 'pydocstyle']},
      dependency_links=open('dependency_links.txt').read().splitlines())
