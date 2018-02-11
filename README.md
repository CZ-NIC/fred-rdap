# FRED: RDAP Server #

The RDAP server is a Django application which provides Registration Data Access Protocol (RDAP)
interface to the FRED registry system.

RDAP succeeds the WHOIS protocol used to query information about domains, contacts
and other domain registry objects, but provides results in a machine-readable format (JSON).

## Dependencies ##
- python 2.7
- python-omniorb
- python-django 1.10 to 1.11
- Other dependencies are listed in [requirements.txt](requirements.txt)

## Installation ##
1. Link `rdap` URLs into your `urls.py`

        urlpatterns += [
           url(r'', include('rdap.urls')),
        ]

    or use RDAP's URLs directly as a `ROOT_URLCONF` in your settings

        ROOT_URLCONF = 'rdap.urls'
