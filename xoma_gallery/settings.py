# Django settings for xoma_gallery project.
import os
from socket import gethostname

try:
    DJANGO_ENV = os.environ['DJANGO_ENV']
except KeyError:
    DJANGO_ENV = 'DEVELOPMENT'

PRODUCTION = gethostname() in ('tonga.xoma.com', 'tonga')
DEBUG = True
TEMPLATE_DEBUG = True

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

#DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
#DATABASE_NAME = 'peripheral'             # Or path to database file if using sqlite3.
#DATABASE_USER = 'mark'             # Not used with sqlite3.
#DATABASE_PASSWORD = ''         # Not used with sqlite3.
#DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
#DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'celldb',
        'USER': 'mark',
        'PASSWORD': 'mark',
        'HOST': '',
        'PORT': '',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True


# From RI productions settings file
#######################################################################################
#SETTINGS_FILE_FOLDER = os.path.realpath(os.path.dirname(__file__))

# Media files (files associated with models)
#MEDIA_ROOT = '/opt/local/var/media'
#MEDIA_URL = '/media/'

# Static files
#STATIC_ROOT = '/opt/local/var/static'
#STATIC_URL = '/static/'
#STATICFILES_DIRS = (os.path.join(SETTINGS_FILE_FOLDER, 'static'),)
#ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
#######################################################################################



# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
SETTINGS_FILE_FOLDER = os.getcwd()+'/xoma_gallery/'
MEDIA_ROOT = os.path.join(SETTINGS_FILE_FOLDER, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
#STATIC_ROOT = os.path.join(SETTINGS_FILE_FOLDER,'static')
STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(SETTINGS_FILE_FOLDER, 'static'),)
ADMIN_MEDIA_PREFIX = STATIC_URL+'admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '_k&bc3$^)1i7^!*wgahk&!79s)7ae0d6mv2r-1gta5h_938+a!'

LOGIN_URL = '/xoma_gallery/contest/login/'
LOGIN_REDIRECT_URL = '/xoma_gallery/contest/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '3ves7%u97m2wx#_s=8@9t2h%x&u-ogn$&cn46x68f4f171rq5v'

SESSION_COOKIE_NAME = 'contestsessionid'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'xoma_gallery.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates"
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(SETTINGS_FILE_FOLDER, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.staticfiles',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.comments',
    'xoma_gallery.decider',
    'xoma_gallery.lib',
    'xoma_gallery.files',
    'xoma_gallery.photos',    
)

if PRODUCTION:
  AD_DNS_NAME = 'xoma.com'
  # If using non-SSL use these
  AD_LDAP_PORT=389
  AD_LDAP_URL='ldap://%s:%s' % (AD_DNS_NAME,AD_LDAP_PORT)
  # If using SSL use these:
  # AD_LDAP_PORT = 636
  # AD_LDAP_URL = 'ldaps://%s:%s' % (AD_DNS_NAME,AD_LDAP_PORT)
  AD_SEARCH_DN = 'dc=xoma,dc=com'
  AD_NT4_DOMAIN = 'xoma.com'
  # AD_MEMBERSHIP_REQ = ['Group_Required', 'Alternative_Group']
  AD_CERT_FILE = '/opt/local/etc/ldap/ca/xoma_standalone_ca-b64-enc.cer'
  AD_CERT_PATH = '/opt/local/etc/ldap/ca/'
  AUTHENTICATION_BACKENDS = ('lib.ldapauth.ActiveDirectorySSLBackend', 
                             'django.contrib.auth.backends.ModelBackend')

  # LDAP_PREBINDDN = 'preclinri@xoma.com'
  # LDAP_PREBINDPW = '2008Xoma1'
