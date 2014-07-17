import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "rdap_cfg"

sys.path = "ROOT_DIR/etc/fred:ROOT_DIR/lib/python2.7/site-packages:ROOT_DIR/lib/python2.7/site-packages/rdap:".split(":") + sys.path

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
