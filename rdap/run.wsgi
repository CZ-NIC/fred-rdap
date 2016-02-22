import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "rdap_cfg"

sys.path = "SYSCONF_DIR:PURELIB_DIR:PURELIB_RDAP_DIR".split(":") + sys.path

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
