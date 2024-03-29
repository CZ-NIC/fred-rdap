.. image:: https://fred.nic.cz/documentation/html/_static/fred-logo.png
   :target: https://fred.nic.cz
   :alt: FRED

=================
FRED: RDAP Server
=================

..

   An RDAP server (front end) prototype implemented with Django

The RDAP server is a Django application which provides Registration Data Access Protocol (RDAP)
interface to the FRED registry system.

RDAP succeeds the WHOIS protocol used to query information about domains, contacts
and other domain registry objects, but provides results in a machine-readable format (JSON).

This repository is a subproject of FRED, the Free Registry for ENUM and Domains,
and it contains only a fraction of the source code required for running FRED.
See the
`complete list of subprojects <https://fred.nic.cz/documentation/html/Architecture/SourceCode.html>`_
that make up FRED.

Learn more about the project and our community on the `FRED's home page <https://fred.nic.cz>`_.

Documentation for the whole FRED project is available on-line, visit https://fred.nic.cz/documentation.

Table of Contents
=================

* `Dependencies <#dependencies>`_
* `Installation <#installation>`_
* `Configuration <#configuration>`_
* `Docker <#docker>`_
* `Development <#development>`_
* `Testing <#testing>`_
* `Maintainers <#maintainers>`_
* `License <#license>`_

Dependencies
============

* python >=3.8
* python-django 3.2, 4.0 and 4.1
* Other dependencies are listed in `setup.cfg <setup.cfg>`_

Installation
============

This application is a standard Django application and is deployed the same way as other application.
Detailed information about deploynment of Django applications can be found at https://docs.djangoproject.com/en/2.2/howto/deployment/.


#. Add ``rdap.apps.RdapAppConfig`` to your ``INSTALLED_APPS``.
#. Link ``rdap`` URLs into your ``urls.py``

   .. code-block::

       urlpatterns += [
          url(r'', include('rdap.urls')),
       ]


    or use RDAP's URLs directly as a ``ROOT_URLCONF`` in your settings

   .. code-block::

       ROOT_URLCONF = 'rdap.urls'

#. According to `RDAP specification, section 5.6 <https://tools.ietf.org/html/rfc7480#section-5.6>`_ it is recommended to set the ``Access-Control-Allow-Origin`` header.
   It may be added by HTTP server or `django-cors-headers <https://github.com/ottoyiu/django-cors-headers>`_ application.

Configuration
=============

Study the example configuration in `examples/rdap_cfg.py <examples/rdap_cfg.py>`_.

RDAP can be configured with the following settings.

``RDAP_LOGGER``
---------------

A dotted path to the logger client.
Default value is ``grill.DummyLoggerClient``.

``RDAP_LOGGER_OPTIONS``
-----------------------

A mapping with options for the ``RDAP_LOGGER``.
If the key ``credentials`` is present, it will be passed to the ``make_credentials`` utility as a mapping.
Default value is ``{}``.

``RDAP_REGISTRY_NETLOC``
------------------------

Network location, i.e. host and port, of the registry server.
This setting is required.

``RDAP_REGISTRY_SSL_CERT``
--------------------------

Path to file with SSL root certificate.
Default value is ``None``, which disables the SSL encryption.

``RDAP_DISCLAIMER``
-------------------

A disclaimer text to be attached to every response.
Valid value is a list of strings, see `RDAP specification, section 4.3 <https://tools.ietf.org/html/rfc7483#section-4.3>`_ for details.
Default value is ``None``\ , i.e. no disclaimer.

``RDAP_UNIX_WHOIS``
-------------------

The host name or IP address of the WHOIS server as defined by `Port 43 WHOIS Server <https://tools.ietf.org/html/rfc7483#section-4.7>`_.
Default value is ``None``\ , i.e. disabled.

``RDAP_MAX_SIG_LIFE``
---------------------

Value of the ``maxSigLife`` member in `the domain object class <https://tools.ietf.org/html/rfc7483#section-5.3>`_.
Default value is ``None``\ , i.e. disabled.

Docker
======

RDAP can be deployed using docker.

To build image use::

    docker build --tag rdap --file docker/uwsgi/Dockerfile .

The image provides a uWSGI service at port 16000 and a volume with static files.
Running the image requires setting a ``SECRET_KEY`` and ``ALLOWED_HOSTS`` environment variables.
RDAP settings can be provided as environment variables as well.

Development
===========

Testing
-------

.. code-block::

   tox

Maintainers
===========

* Vlastimil Zíma `vlastimil.zima@nic.cz <vlastimil.zima@nic.cz>`_
* Tomáš Pazderka `tomas.pazderka@nic.cz <tomas.pazderka@nic.cz>`_
* Jaromír Talíř `jaromir.talir@nic.cz <jaromir.talir@nic.cz>`_
