import os
import sys

path = '/home/shreejoy'
if path not in sys.path:
   sys.path.append(path)
path = '/home/shreejoy/biophysiome'
if path not in sys.path:
   sys.path.append(path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'biophysiome.settings'

import biophysiome.settings
import nltk

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

