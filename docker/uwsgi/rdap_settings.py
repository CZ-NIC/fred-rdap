"""Settings of RDAP project"""
import logging
import os
import socket
from email.utils import getaddresses
from http import HTTPStatus

import environ
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import ignore_logger

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

env = environ.Env()

###############################################################################
# Basic settings
SECRET_KEY = env.str('SECRET_KEY')

ADMINS = getaddresses([env.str('ADMINS', default='')])

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

DEBUG = env.bool('DEBUG', default=False)

###############################################################################
# Application
INSTALLED_APPS = [
    'rdap.apps.RdapAppConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'rdap.urls'

###############################################################################
# Email settings
#
# Only for error emails.
if 'EMAIL_HOST' in env:
    EMAIL_HOST = env.str('EMAIL_HOST')
if 'EMAIL_HOST_USER' in env:
    EMAIL_HOST_USER = env.str('EMAIL_HOST_USER')
if 'EMAIL_HOST_PASSWORD' in env:
    EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD')
if 'EMAIL_PORT' in env:
    EMAIL_PORT = env.int('EMAIL_PORT')
EMAIL_SUBJECT_PREFIX = '[rdap@{}]: '.format(env.str('ENVIRONMENT', default=socket.gethostname()))
SERVER_EMAIL = env.str('SERVER_EMAIL', default='rdap@{}'.format(env.str('ENVIRONMENT', default=socket.gethostname())))

###############################################################################
# Security
SECURE_SSL_REDIRECT = True

###############################################################################
# RDAP specific settings can be set in environment.
# See django-appsettings on how envirnment variables are handled.

###############################################################################
# Locale settings
USE_TZ = True
TIME_ZONE = env.str('TIME_ZONE', default='UTC')


###############################################################################
# Logging
#
# Log are printed to stdout, to be processed by docker.
def skip_not_implemented(record: logging.LogRecord):
    """Skip records triggered by 'Not Implemented' HTTP status."""
    return getattr(record, 'status_code', None) != HTTPStatus.NOT_IMPLEMENTED


def skip_disallowed_host(record: logging.LogRecord):
    """Skip records triggered by DisallowedHost."""
    return record.name != 'django.security.DisallowedHost'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'skip_not_implemented': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': skip_not_implemented,
        },
        'skip_disallowed_host': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': skip_disallowed_host,
        },
    },
    'formatters': {
        'verbose': {'format': '%(asctime)s %(levelname)-8s %(module)s:%(funcName)s:%(lineno)s %(message)s'},
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['skip_not_implemented', 'skip_disallowed_host'],
            'include_html': True,
        },
        'stdout': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['stdout', 'mail_admins'],
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
        # Override django logger to only propagate logs to root logger.
        'django': {
            'propagate': True,
        },
    },
}

# Configure Sentry
if 'SENTRY_DSN' in env:
    sentry_sdk.init(
        dsn=env.str('SENTRY_DSN'),
        environment=env.str('ENVIRONMENT', default=None),
        integrations=[DjangoIntegration()],
        send_default_pii=True,
        ca_certs=env.str('SENTRY_CA_CERTS', default=None),
    )
    ignore_logger("django.security.DisallowedHost")
