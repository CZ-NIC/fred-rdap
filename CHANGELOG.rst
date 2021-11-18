=========
Changelog
=========

Unreleased
----------

1.0.2 (2021-11-18)
------------------

* Fix Fedora packages.

1.0.1 (2021-02-17)
------------------

* Fix bug in dependencies limiting Django to 3.0.

1.0.0 (2020-10-01)
------------------

* Drop Python 2.7 support.
* Add Python 3.8 and 3.9 support.
* Add Django 3.0 and 3.1 support.
* Add ``RDAP_LOGGER_CORBA_OBJECT`` setting.
* Add simple benchmark.
* Fix deprecations from pylogger.
* Update style checks, add mypy.
* Update CI setup.
* Fix rc style in bumpversion.
* Reformat and rename README and CHANGELOG to ReST.
* Fix tests for python 3.8.

0.16.0 (2019-11-19)
-------------------

* Add mapping for EPP statuses (RFC 8056).
* Refacotr code and drop ``RDAP_ROOT_URL`` setting.
* Rename setting ``DNS_MAX_SIG_LIFE`` to ``RDAP_MAX_SIG_LIFE`` and allow it to be ``None``.
* Update README.
* Update CI and tests configuration.
* Use bumpversion to bump version.

0.15.0 (2019-10-23)
-------------------

* Add Django 2.X support.
* Use PEP 508 dependencies.
* Update CI and setup configuration.

0.14.0 (2019-03-20)
-------------------

* License GNU GPLv3+
* Disclaimer setting reworked
* Test fixes
* CI fixes

0.13.0 (2018-07-20)
-------------------

* Add Python 3 and Django 2.0 support.
* Use ``appsettings`` for Corba settings.
* Rename ``UNIX_WHOIS_HOST`` setting to ``RDAP_UNIX_WHOIS``.
* Update help responses.
* Fix Fedora builds.
* Remove manage.py file.

0.12.0 (2018-04-17)
-------------------

* Drop support for old IDL structures
* Use tox for testing

0.11.1 (2018-04-17)
-------------------

* Fix response for domains in delete candidate status.

0.11.0 (2018-03-08)
-------------------

* Prepare for Python 3 - clean up code and use ``unicode_literals``.
* Support new ISO date time structures from IDLs.
* Fix RPM builds

0.10.0 (2018-02-12)
-------------------

* Remove CORS headers from the rdap application itself.
* Add README
* Add conformance tests to CI

0.9.0 (2017-12-20) 
------------------

* Drop support for Django < 1.10.
* Use statically compiled IDL modules.
* Use pyfco Client for Corba calls.
* Development tools and CI update.

0.8.0 (2017-11-14)
------------------

* Use ``setuptools`` for distribution.
* Development tools and CI update.

0.7.0 (2017-08-18)
------------------

* Use pyfco utilities for Corba.
* Refactor link creation and drop ``RDAP_ENTITY_URL_TMPL`` setting.
* Support Django 1.11.
* Move exceptions to ``rdap.exceptions`` module.
* Move corba utilities to ``rdap.utils.corba`` module.
* Drop ``rdap.utils.py_logging`` module.
* Development tools and CI update.

0.6.0 (2017-04-03)
------------------

* CI and requirements changes/fixes

0.5.0 (2017-03-02)
------------------

* django 1.10 compatibility changes
* CI changes/fixes (coverage)

0.4.2 (2017-03-07)
-----------------

* fedora packaging

0.4.1 (2016-12-19)
------------------

* disable csrf check on rdap views
* add comments to configuration file

0.4.0 (2016-10-27)
------------------

* removed django rest framework

0.3.3 (2016-05-12)
------------------

* resolve error when django-guardian is installed

0.3.2 (2016-03-30)
------------------

* fix rpm - missing dependency on python-idna

0.3.1 (2016-03-22)
------------------

* fix rpm build
* patch corba recoder for omniorb 4.2.0
* add logging setup to config

0.3.0 (2016-01-20)
------------------

* changes according to rfc document standardization

0.2.0 (2015-01-27)
------------------

* show 'delete pending' status for domains scheduled for deletion

0.1.1 (2014-09-03)
------------------

* add optional disclaimer text from file (settings)

0.1.0 (2014-08-01)
------------------

* prototype of RDAP implementation for FRED registry system
   * implemented queries for - entity, domain, nameserver
   * extension for FRED specific types - ``cznic_nsset``, ``cznic_keyset``
   * used drafts:
      * http://tools.ietf.org/html/draft-ietf-weirds-rdap-query-10
      * http://tools.ietf.org/html/draft-ietf-weirds-json-response-07
      * http://tools.ietf.org/html/draft-ietf-weirds-using-http-08
