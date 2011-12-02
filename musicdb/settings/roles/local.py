DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = ()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
        'NAME': 'musicdb.sqlite',             # Or path to database file if using sqlite3.
        'USER': '',             # Not used with sqlite3.
        'PASSWORD': '',         # Not used with sqlite3.
        'HOST': '',             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',             # Set to empty string for default. Not used with sqlite3.
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

SITE_URL = 'http://127.0.0.1:8000'
STATIC_MEDIA_URL = '/media/%(path)s'
