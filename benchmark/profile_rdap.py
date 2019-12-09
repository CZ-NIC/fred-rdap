#!/usr/bin/python3
"""Perform a RDAP benchmark on a domain URL."""
from __future__ import unicode_literals

import cProfile
import itertools
import string

import django
from django.test import RequestFactory
from pylogger.dummylogger import DummyLogger

from rdap import views
from rdap.rdap_rest.whois import get_domain_by_handle

django.setup()


DOMAIN_CHARS = string.ascii_lowercase + string.digits


def generate_domains():
    for length in range(1, 2):
        for label in itertools.product(DOMAIN_CHARS, repeat=length):
            yield ''.join(label) + '.cz'


def execute(func, args_list):
    for args in args_list:
        func(*args)


def main():
    view = views.FqdnObjectView.as_view(getter=get_domain_by_handle, request_type='DomainLookup')
    request = RequestFactory().get('/dummy/')
    print("Run profile with logging.")
    kwargs = {'func': view,
              'args': tuple((request, domain) for domain in generate_domains())}
    cProfile.runctx('execute(func, args)', globals(), kwargs, sort='cumulative')
    print("Run profile without logging.")
    views.LOGGER = DummyLogger()
    kwargs = {'func': view,
              'args': tuple((request, domain) for domain in generate_domains())}
    cProfile.runctx('execute(func, args)', globals(), kwargs, sort='cumulative')


if __name__ == '__main__':
    main()
