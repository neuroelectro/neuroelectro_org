import sys
import os

URL_PREFIX = '/brenna'
CODE_DIR = "/Users/brenna/git/neuroelectro_org/db_functions"
sys.path.append(CODE_DIR)
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Brenna Li', 'brenna.li430@gmail.com'),
)

#MEDIA_ROOT = '/home/stripathy/neuroelectro_org/neuroelectro/media/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'neuroelectro',                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

INTERNAL_IPS = ['127.0.0.1']

# API Key for use of elsevier text-mining API - currently works on CMUs network
ELS_API_KEY = '0ebfe3f2ed341d2086585f01e64a937a'

# API KEY for use of the entrez ajax app: https://entrezajax.appspot.com/
ENTREZ_AJAX_API_KEY = '3a8a2ce117a029a0b896eafa85e412b0'

# Distinguishes between production and testing environments
neuroelectro_VERSION = 'DEV'

ADMIN_EMAIL_ADDRESS = 'neuroelectro.adm@gmail.com'
ADMIN_EMAIL_PASSWORD = 'lilahisthebest'

STATIC_ROOT = "/Users/brenna/Documents/neuroelectrostatic/"

# Additional locations of static files
STATICFILES_DIRS = (
    # Don't forget to use absolute paths, not relative paths.
    '/Users/brenna/Documents/neuroelectro_org/neuroelectro_org/neuroelectro/static/',
)

SECRET_KEY = '=z*vh(083flhj(+&@59u%v5e%qc7mj1i21rqfau9i!b*@w=^)s'
SOCIAL_AUTH_GOOGLE_PLUS_SECRET = 'pDPjYOiEkRV26sUj_valjThp'
MORE_ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '127.0.0.1:8000', 'localhost:8000']
OUTPUT_FILES_DIRECTORY = '/Users/brenna/Documents/Neuroelectro documents/'
