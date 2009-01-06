from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('musicdb.classical.views',
    url(r'^$', 'index', name='classical'),
    url(r'^stats/$', 'stats', name='classical-stats'),
    url(r'^timeline/$', 'timeline', name='classical-timeline'),
    url(r'^timeline/data$', 'timeline_data', name='classical-timeline-data'),

    url(r'^artist/timeline/(?P<slug>[^/]+)$', 'artist_timeline', name='classical-artist-timeline'),
    url(r'^artist/timeline/(?P<slug>[^/]+)/data$', 'artist_timeline_data', name='classical-artist-timeline-data'),

    url(r'^artist/(?P<slug>[^/]+)$', 'artist', name='classical-artist'),
    url(r'^artist/(?P<artist_slug>[^/]+)/(?P<slug>[^/]+)$', 'work', name='classical-work'),
    url(r'^ensemble/(?P<slug>[^/]+)$', 'ensemble', name='classical-ensemble'),

)
