from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('musicdb.nonclassical.views',
    url(r'^$', 'index', name='nonclassical', kwargs={'letter': None}),
    url(r'^(?P<letter>[a-z-0])$', 'index', name='nonclassical-letter'),
    url(r'^(?P<slug>[^/]+)$', 'artist', name='nonclassical-artist'),
    url(r'^(?P<artist_slug>[^/]+)/(?P<slug>[^/]+)$', 'album', name='nonclassical-album'),
)
