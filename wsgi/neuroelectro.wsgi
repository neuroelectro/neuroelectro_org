import os
import sys

path = '/home/shreejoy'
if path not in sys.path:
   sys.path.append(path)
path = '/home/shreejoy/neuroelectro_org'
if path not in sys.path:
   sys.path.append(path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'neuroelectro_org.settings'

import neuroelectro_org.settings

neuroelectro_org.settings.ROOT_URLCONF = 'neuroelectro_org.urls'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

