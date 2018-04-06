[![FRED](https://fred.nic.cz/documentation/html/_static/fred-logo.png)](https://fred.nic.cz)

# FRED: RDAP Server #

> An RDAP server (front end) prototype implemented with Django

The RDAP server is a Django application which provides Registration Data Access Protocol (RDAP)
interface to the FRED registry system.

RDAP succeeds the WHOIS protocol used to query information about domains, contacts
and other domain registry objects, but provides results in a machine-readable format (JSON).

This repository is a subproject of FRED, the Free Registry for ENUM and Domains,
and it contains only a fraction of the source code required for running FRED.
See the
[complete list of subprojects](https://fred.nic.cz/documentation/html/Architecture/SourceCode.html)
that make up FRED.

Learn more about the project and our community on the [FRED's home page](https://fred.nic.cz).

Documentation for the whole FRED project is available on-line, visit https://fred.nic.cz/documentation.

## Table of Contents ##
- [Dependencies](#dependencies)
- [Installation](#installation)
- [Configuration](#configuration)
- [Development](#development)
    - [Testing](#testing)
- [Maintainers](#maintainers)
- [License](#license)

## Dependencies ##
- python 2.7
- python-omniorb
- python-django 1.10 to 2.2
- Other dependencies are listed in [requirements.txt](requirements.txt)

## Installation ##
This application is a standard Django application and is deployed the same way as other application.
Detailed information about deploynment of Django applications can be found at https://docs.djangoproject.com/en/2.2/howto/deployment/.

1. Add `rdap.apps.RdapAppConfig` to your `INSTALLED_APPS`.
2. Link `rdap` URLs into your `urls.py`

        urlpatterns += [
           url(r'', include('rdap.urls')),
        ]

    or use RDAP's URLs directly as a `ROOT_URLCONF` in your settings

        ROOT_URLCONF = 'rdap.urls'

3. According to [RDAP specification](https://tools.ietf.org/html/rfc7480#section-5.6) it is recommended to set the `Access-Control-Allow-Origin` header.
   It may be added by HTTP server or [django-cors-headers](https://github.com/ottoyiu/django-cors-headers) application.

## Configuration ##
Study the example configuration in [examples/rdap_cfg.py](examples/rdap_cfg.py).

### Settings ###
RDAP can be configured with a following settings.

#### `RDAP_CORBA_NETLOC` ####

Network location, i.e. host and port, of the CORBA server.
Used to construct Interoperable Object Reference (IOR).
Default value is ``localhost``.

#### `RDAP_CORBA_CONTEXT` ####

The name of the RDAP CORBA context.
Default value is ``fred``.

#### `RDAP_DISCLAIMER` ####

A disclaimer text to be attached to every response.
Valid value is a list of strings, see [RDAP specification](https://tools.ietf.org/html/rfc7483#section-4.3) for details.
Default value is ``None``, i.e. no disclaimer.

#### `RDAP_UNIX_WHOIS` ####

The host name or IP address of the WHOIS server as defined by [Port 43 WHOIS Server](https://tools.ietf.org/html/rfc7483#section-4.7).
Default value is ``None``, i.e. disabled.

## Development ##

### Testing ###
```
tox
```

## Maintainers ##
- Vlastimil Zíma [vlastimil.zima@nic.cz](vlastimil.zima@nic.cz)
- Tomáš Pazderka [tomas.pazderka@nic.cz](tomas.pazderka@nic.cz)
- Jaromír Talíř [jaromir.talir@nic.cz](jaromir.talir@nic.cz)
