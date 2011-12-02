from setup_warnings import *

from os.path import abspath, dirname, join

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Chris Lamb', 'chris@chris-lamb.co.uk'),
)
MANAGERS = ADMINS

INTERNAL_IPS = ('127.0.0.1',)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'musicdb',
        'USER': 'root',
        'PASSWORD': 'password',
        'HOST': '',
        'PORT': '',
    }
}

MUSICDB_BASE_PATH = dirname(dirname(dirname(dirname(abspath(__file__)))))

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = False

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = ''

STATIC_MEDIA_URL = '/media/%(hash).6s/%(path)s'
STATIC_MEDIA_ROOT = join(MUSICDB_BASE_PATH, 'media')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'musicdb.urls'

TEMPLATE_DIRS = (
    join(MUSICDB_BASE_PATH, 'templates'),
)

FUSE_URLCONF = 'fuse_urls'

DEBUG_TOOLBAR_CONFIG = {
    'HIDE_DJANGO_SQL': True,
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TEMPLATE_CONTEXT': False,
}

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',

    'debug_toolbar',
    'django_extensions',
    'django_fuse',
    'treebeard',

    'musicdb.common',
    'musicdb.classical',
    'musicdb.nonclassical',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'gh*w7@sdfj4%i=xyjatf_@!wx^d#tam^&5q6(f=z6io-302iwu'

MEDIA_ROOT = 'site_media'
MEDIA_URL = '/site_media/'

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'KEY_PREFIX': 'musicdb',
    }
}

SITE_URL = 'http://musicdb.chris-lamb.co.uk/'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
)

LOGIN_URL = '/login'
