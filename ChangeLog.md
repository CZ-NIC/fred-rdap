2019-03-20 (0.14.0)

 * License GNU GPLv3+
 * Disclaimer setting reworked
 * Test fixes
 * CI fixes

2018-07-20 (0.13.0)

 * Add Python 3 and Django 2.0 support.
 * Use ``appsettings`` for Corba settings.
 * Rename ``UNIX_WHOIS_HOST`` setting to ``RDAP_UNIX_WHOIS``.
 * Update help responses.
 * Fix Fedora builds.
 * Remove manage.py file.

2018-04-17 (0.12.0)

 * Drop support for old IDL structures
 * Use tox for testing

2018-04-17 (0.11.1)

 * Fix response for domains in delete candidate status.

2018-03-08 (0.11.0)

 * Prepare for Python 3 - clean up code and use ``unicode_literals``.
 * Support new ISO date time structures from IDLs.
 * Fix RPM builds

2018-02-12 (0.10.0)

 * Remove CORS headers from the rdap application itself.
 * Add README
 * Add conformance tests to CI

2017-12-20 (0.9.0)

 * Drop support for Django < 1.10.
 * Use statically compiled IDL modules.
 * Use pyfco Client for Corba calls.
 * Development tools and CI update.

2017-11-14 (0.8.0)

 * Use ``setuptools`` for distribution.
 * Development tools and CI update.

2017-08-18 (0.7.0)

 * Use pyfco utilities for Corba.
 * Refactor link creation and drop ``RDAP_ENTITY_URL_TMPL`` setting.
 * Support Django 1.11.
 * Move exceptions to ``rdap.exceptions`` module.
 * Move corba utilities to ``rdap.utils.corba`` module.
 * Drop ``rdap.utils.py_logging`` module.
 * Development tools and CI update.

2017-04-03 (0.6.0)

 * CI and requirements changes/fixes

2017-03-02 (0.5.0)

  * django 1.10 compatibility changes
  * CI changes/fixes (coverage)

2017-03-07 (0.4.2)

  * fedora packaging

2016-12-19 (0.4.1)

  * disable csrf check on rdap views
  * add comments to configuration file

2016-10-27 (0.4.0)

  * removed django rest framework

2016-05-12 (0.3.3)

  * resolve error when django-guardian is installed

2016-03-30 (0.3.2)

  * fix rpm - missing dependency on python-idna

2016-03-22 (0.3.1)

  * fix rpm build
  * patch corba recoder for omniorb 4.2.0
  * add logging setup to config

2016-01-20 (0.3.0)

  * changes according to rfc document standardization

2015-01-27 (0.2.0)

  * show 'delete pending' status for domains scheduled for deletion

2014-09-03 (0.1.1)

  * add optional disclaimer text from file (settings)

2014-08-01 (0.1.0)

  * prototype of RDAP implementation for FRED registry system
    - implemented queries for - entity, domain, nameserver
    - extension for FRED specific types - ``cznic_nsset``, ``cznic_keyset``
    - used drafts:
      - http://tools.ietf.org/html/draft-ietf-weirds-rdap-query-10
      - http://tools.ietf.org/html/draft-ietf-weirds-json-response-07
      - http://tools.ietf.org/html/draft-ietf-weirds-using-http-08
