URL_PREFIX = '/shreejoy'
CODE_DIR = '/Users/stripathy/neuroelectro_org/code'
import sys
sys.path.append(CODE_DIR)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'neuroelectro',                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': '***REMOVED***',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

ELS_API_KEY = '***REMOVED***'