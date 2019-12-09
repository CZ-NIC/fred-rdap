#!/usr/bin/python3
"""
Perform a RDAP benchmark on a domain URL.

Usage: profile_rdap.py [options] <url>
       profile_rdap.py -h | --help

Options:
  -h, --help           show this help message and exit
  -c, --client         use Django test client [default]
  -r, --requests       use requests
"""
import cProfile
import itertools
import string
from urllib.parse import urljoin

import requests
from docopt import docopt


DOMAIN_CHARS = string.ascii_lowercase + string.digits


def generate_domains():
    for length in range(1, 3):
        for label in itertools.product(DOMAIN_CHARS, repeat=length):
            yield ''.join(label) + '.cz'


def execute(func, args_list):
    for args in args_list:
        func(*args)


def main():
    options = docopt(__doc__)

    kwargs = {'func': requests.get,
              'args': tuple((urljoin(options['<url>'], domain), ) for domain in generate_domains())}
    cProfile.runctx('execute(func, args)', globals(), kwargs, sort='cumulative')


if __name__ == '__main__':
    main()
