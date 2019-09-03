# FRED: RDAP Server #

The RDAP server is a Django application which provides Registration Data Access Protocol (RDAP)
interface to the FRED registry system.

RDAP succeeds the WHOIS protocol used to query information about domains, contacts
and other domain registry objects, but provides results in a machine-readable format (JSON).

## Dependencies ##
- python 2.7
- python-omniorb
- python-django 1.10 to 2.2
- Other dependencies are listed in [requirements.txt](requirements.txt)

## Installation ##
1. Add `rdap.apps.RdapAppConfig` to your `INSTALLED_APPS`.
2. Link `rdap` URLs into your `urls.py`

        urlpatterns += [
           url(r'', include('rdap.urls')),
        ]

    or use RDAP's URLs directly as a `ROOT_URLCONF` in your settings

        ROOT_URLCONF = 'rdap.urls'

3. According to [RDAP specification](https://tools.ietf.org/html/rfc7480#section-5.6) it is recommended to set the `Access-Control-Allow-Origin` header.
   It may be added by HTTP server or [django-cors-headers](https://github.com/ottoyiu/django-cors-headers) application.

## Settings ##
RDAP can be configured with a following settings.

### `RDAP_CORBA_NETLOC` ###

Network location, i.e. host and port, of the CORBA server.
Used to construct Interoperable Object Reference (IOR).
Default value is ``localhost``.

### `RDAP_CORBA_CONTEXT` ###

The name of the RDAP CORBA context.
Default value is ``fred``.

### `RDAP_DISCLAIMER` ###

A disclaimer text to be attached to every response.
Valid value is a list of strings, see [RDAP specification](https://tools.ietf.org/html/rfc7483#section-4.3) for details.
Default value is ``None``, i.e. no disclaimer.

### `RDAP_UNIX_WHOIS` ###

The host name or IP address of the WHOIS server as defined by [Port 43 WHOIS Server](https://tools.ietf.org/html/rfc7483#section-4.7).
Default value is ``None``, i.e. disabled.
