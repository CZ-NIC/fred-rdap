#!/usr/bin/python
#
# Copyright (C) 2014-2021  CZ.NIC, z. s. p. o.
#
# This file is part of FRED.
#
# FRED is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FRED is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FRED.  If not, see <https://www.gnu.org/licenses/>.

from setuptools import find_packages, setup


setup(name='fred-rdap',
      description='NIC.CZ RDAP',
      version='1.0.0-rc3',
      author='Jan Korous, CZ.NIC',
      author_email='jan.korous@nic.cz',
      url='http://www.nic.cz/',
      license='GPLv3+',
      platforms=['posix'],
      long_description='CZ.NIC RDAP server',
      packages=find_packages(),
      include_package_data=True,
      install_requires=open('requirements.txt').read().splitlines(),
      extras_require={'quality': ['isort', 'flake8', 'pydocstyle', 'mypy']})
