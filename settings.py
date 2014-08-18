import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)),"codeproject"))

# Django settings for neuroelectro_org project.

ADMINS = (
    ('Shreejoy Tripathy', 'stripat3@gmail.com')
)

MANAGERS = ADMINS

# the actual database info gets imported from local_settings.py - an untracked file
DATABASES = {
}

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '127.0.0.1:8000', 'localhost:8000', u'137.82.232.158', u'www.google.com', u'pavlab', '.kent.pavlab.chibi.ubc.ca', 'kent.pavlab.chibi.ubc.ca.', 'neuroelectro.org', 'www.neuroelectro.org', ]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'
USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

URL_PREFIX = ''

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    #'/C:/Users/Shreejoy/Desktop/neuroelectro_org/neuroelectro/static/',
    #'/home/shreejoy/neuroelectro_org/neuroelectro/static/'
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    #'/Users/dtebaykin/Documents/workspace/neuroelectro_org/neuroelectro_org/neuroelectro/static/',
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '=z*vh(083flhj(+&@59u%v5e%qc7mj1i21rqfau9i!b*@w=^)s'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

LOGIN_REDIRECT_URL = '/'

# Open Authentication Stuff. 
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    'django.core.context_processors.request',
    'social_auth.context_processors.social_auth_by_name_backends',
    'social_auth.context_processors.social_auth_backends',
    'social_auth.context_processors.social_auth_by_type_backends',
    'zinnia.context_processors.version'
)
 
AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    #'social_auth.backends.google.GoogleOAuthBackend',
    #'social_auth.backends.google.GoogleOAuth2Backend',
    'social_auth.backends.google.GoogleBackend',
    'django.contrib.auth.backends.ModelBackend',
)

TWITTER_CONSUMER_KEY         = 'YaI9bCRNTJPaRjsnTNfYw'
TWITTER_CONSUMER_SECRET      = 'gCjicazw9SiJGfiFrpxeIAiMEWRCFWCD33iyvWrIo'
GOOGLE_CONSUMER_KEY          = ''
GOOGLE_CONSUMER_SECRET       = ''
#GOOGLE_OAUTH2_CLIENT_ID      = ''
#GOOGLE_OAUTH2_CLIENT_SECRET  = ''
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

SOCIAL_AUTH_DEFAULT_USERNAME = 'new_social_auth_user'
#SOCIAL_AUTH_USER_MODEL = 'neuroelectro.User'

CRISPY_TEMPLATE_PACK = 'bootstrap' 

CKEDITOR_UPLOAD_PATH = "." + MEDIA_URL
CKEDITOR_CONFIGS = {
           'default': {
               'toolbar': 'Full',
           },
       }
CKEDITOR_RESTRICT_BY_USER = "True"

AUTH_USER_MODEL = 'neuroelectro.User'

USE_SOCIAL_AUTH_AS_ADMIN_LOGIN = True

# Middlewares.  
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'neuroelectro_org.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
#    os.path.join(os.path.basename(__file__), 'templates'),
    'html_templates',
)

INSTALLED_APPS = (
    'django_extensions',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.comments',
    'django.contrib.admin',
    'tagging',
    'mptt',
    'zinnia',
    'neuroelectro',
    'neurotree',
    'south',
    'tastypie',
    'crispy_forms',
    'social_auth',
    'ckeditor'
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
#     'handlers': {
#         'mail_admins': {
#             'level': 'ERROR',
#             'filters': ['require_debug_false'],
#             'class': 'django.utils.log.AdminEmailHandler'
#         },
#         'default': {
#             'level': 'ERROR',
#             'class': 'logging.FileHandler',
#             'filename': 'logs/debug.log',
#         },
#     },
#     'loggers': {
#         'django.request': {
#             'handlers': ['mail_admins', 'default'],
#             'level': 'ERROR',
#             'propagate': True,
#         },
#     }
}

try:
    from local_settings import *
except ImportError:
    pass
