#
# Copyright (C) 2014-2018  CZ.NIC, z. s. p. o.
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

"""Wrapper module to whois idl interface."""
from __future__ import unicode_literals

import logging

from django.conf import settings
from django.urls import reverse
from six.moves.urllib.parse import urljoin

from .rdap_utils import ObjectClassName, add_unicode_name


def nameserver_to_dict(struct):
    """Transform CORBA nameserver struct to python dictionary."""
    logging.debug(struct)

    if struct is None:
        result = None
    else:
        self_link = urljoin(settings.RDAP_ROOT_URL, reverse('nameserver-detail', kwargs={"handle": struct.fqdn}))

        result = {
            "rdapConformance": ["rdap_level_0"],
            "objectClassName": ObjectClassName.NAMESERVER,
            "handle": struct.fqdn,
            "ldhName": struct.fqdn,
            "links": [
                {
                    "value": self_link,
                    "rel": "self",
                    "href": self_link,
                    "type": "application/rdap+json",
                },
            ],
        }

        add_unicode_name(result, struct.fqdn)

    logging.debug(result)
    return result
