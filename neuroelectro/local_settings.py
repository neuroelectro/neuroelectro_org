import os
from os.path import expanduser
USER_HOME = expanduser("~")
NEUROELECTRO_HOME = os.path.join(USER_HOME,'.neuroelectro')
if not os.path.exists(NEUROELECTRO_HOME):
    os.mkdir(NEUROELECTRO_HOME)
DB_HOME = os.path.join(NEUROELECTRO_HOME,'neuroelectro.db')

DATABASES = {
    'default': {
	'ENGINE': 'django.db.backends.sqlite3',
         'NAME': DB_HOME,            
    }
}

