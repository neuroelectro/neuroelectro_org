import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

TIME_ZONE = 'Canada/Pacific'
USE_TZ = True
SITE_ID = 1
SECRET_KEY = ' '
USE_I18N = True
USE_L10N = True
AUTH_USER_MODEL = 'neuroelectro.User'
MIDDLEWARE_CLASSES = []
INSTALLED_APPS = (
    'django_extensions',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'neuroelectro',
    'simple_history',
)

try:
    from local_settings import *
except ImportError as e:
    raise e

