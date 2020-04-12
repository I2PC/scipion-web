#===============================================================================
# Django settings for ScipionWeb project.
#===============================================================================

import os
from os.path import dirname, realpath, join
import pyworkflow as pw
import pyworkflow.config as pwconfig

DIRECTORY_PROJECT = dirname(realpath(__file__))
DB_PATH = join(pw.HOME, 'web', 'scipion_web.db')

WEB_CONF = pwconfig.loadWebConf()

DEBUG = True
#DEBUG = WEB_CONF['DEBUG']
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
    ('scipion', WEB_CONF['ADMIN_EMAIL']),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': DB_PATH,  # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',  # Set to empty string for default.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']
# ALLOWED_HOSTS = ['localhost']

SITE_URL = WEB_CONF['SITE_URL']
# Subdomain where Scipion is hosted or working, can't start with a slash: m/
ABSOLUTE_URL = WEB_CONF['ABSOLUTE_URL']
# Populate analytics script into DJANGO settings from .conf file.
ANALYTICS_SCRIPT = WEB_CONF['ANALYTICS_SCRIPT']

WEB_LOG_FILE = WEB_CONF['WEB_LOG_FILE']

# ABSOLUTE_URL = '/examples'

# URL_REDIRECTS = (
#         (r'www\.example\.com/hello/$', 'http://hello.example.com/'),
#         (r'www\.example2\.com/$', 'http://www.example.com/example2/'),
#         (r'asimov.cnb.csic.es/$', 'http://asimov.cnb.csic.es/%s/$' % ABSOLUTE_URL),
#     )


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Madrid'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"

MEDIA_ROOT = os.path.join(pw.HOME, 'resources')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ABSOLUTE_URL + 'resources/'

# Temporary folder where store the files after do a upload
FILE_UPLOAD_TEMP_DIR = MEDIA_ROOT

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = 'static'

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = ABSOLUTE_URL + 'static/'

# Additional locations of static files
WS_ROOT = os.path.join(pw.HOME, 'web', 'webtools')
serviceFolders = [os.path.join(WS_ROOT, f) for f in os.listdir(WS_ROOT)
                  if os.path.isdir(os.path.join(WS_ROOT, f))]
staticDirs = [os.path.join(pw.HOME, 'web', 'pages')] \
            + serviceFolders

# Put strings here, like "/home/html/static" or "C:/www/django/static".
# Always use forward slashes, even on Windows.
# Don't forget to use absolute paths, not relative paths.
STATICFILES_DIRS = tuple([os.path.join(d, 'resources') for d in staticDirs])        

# STATICFILES_DIRS = (
#       os.path.join(pw.HOME, 'web', 'pages', 'resources'),
#       os.path.join(pw.HOME, 'web', 'webservices', 'myfirstmap', 'resources'),
#       os.path.join(pw.HOME, 'web', 'webservices', 'desktop', 'resources'),
# )

# Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
# Always use forward slashes, even on Windows.
# Don't forget to use absolute paths, not relative paths.
templateDirs = [os.path.join(DIRECTORY_PROJECT)] + serviceFolders
templateDirs += [os.path.join(pw.HOME, 'web', 'workflowarchive')]

TEMPLATE_DIRS = tuple([os.path.join(d, 'templates') for d in templateDirs])

# TEMPLATE_DIRS = (
#     os.path.join(DIRECTORY_PROJECT, 'templates'),
#     os.path.join(pw.HOME, 'web', 'webservices', 'myfirstmap', 'templates'),
#     os.path.join(pw.HOME, 'web', 'webservices', 'desktop', 'templates'),
# )

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '@#%2f*5p!fyr2iqhk%#@9c^34p^*x#4&n()ucv2*jf*b3hje0='

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
#     'pyworkflow.web.app.middleware.UrlRedirectMiddleware',
)

SESSION_ENGINE = (
    'django.contrib.sessions.backends.cache'
)
   
ROOT_URLCONF = 'pages.prefix_urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'pages.wsgi.application'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    # 'django.contrib.admindocs',
    # 'gunicorn',
    'app',
    'resumable',
    'workflowarchive',# workflow archive project
    'tastypie',# web services support
]

try:
    import imp
    imp.find_module('gunicorn')
    INSTALLED_APPS.append('gunicorn')
except ImportError:
    pass
    #print "gunicorn not found"

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
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
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': WEB_LOG_FILE
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

APPEND_SLASH = False


# EMAIL configuration

EMAIL_CONF = pwconfig.loadEmailConf()

EMAIL_USE_TLS = EMAIL_CONF['EMAIL_USE_TLS']
EMAIL_HOST = EMAIL_CONF['EMAIL_HOST']
EMAIL_PORT = EMAIL_CONF['EMAIL_PORT']
EMAIL_HOST_USER = EMAIL_CONF['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = EMAIL_CONF['EMAIL_HOST_PASSWORD']
