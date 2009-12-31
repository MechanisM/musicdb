from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('musicdb.common.views',
    url(r'^play/(?P<music_file_id>\d+)$', 'play_music_file',
        name='play-music-file'),
    url(r'^stats$', 'stats',
        name='stats'),
)
