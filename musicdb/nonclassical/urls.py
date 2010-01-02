from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('musicdb.nonclassical.views',
    url(r'^$', 'index', name='nonclassical', kwargs={'letter': None}),
    url(r'^collage$', 'collage', name='nonclassical-collage'),
    url(r'^(?P<letter>[a-z-0])$', 'index', name='nonclassical-letter'),
    url(r'^(?P<slug>[^/]+)$', 'artist', name='nonclassical-artist'),
    url(r'^(?P<artist_slug>[^/]+)/(?P<slug>[^/]+)$', 'album', name='nonclassical-album'),
    url(r'^play/cd/(?P<cd_id>\d+)$', 'play_cd', name='nonclassical-play-cd'),
    url(r'^play/album/(?P<album_id>\d+)$', 'play_album', name='nonclassical-play-album'),
)
