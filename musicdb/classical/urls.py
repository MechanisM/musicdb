from django.conf.urls.defaults import *

urlpatterns = patterns('musicdb.classical.views',
    url(r'^$', 'index', name='classical'),

    url(r'^composers/$', 'composers', name='classical-composers'),
    url(r'^artists/$', 'artists', name='classical-artists'),
    url(r'^ensembles/$', 'ensembles', name='classical-ensembles'),

    url(r'^categories/$', 'categories', name='classical-categories'),
    url(r'^category/(?P<category_slug>[^/]+)$', 'category', name='classical-category'),

    url(r'^stats/$', 'stats', name='classical-stats'),
    url(r'^timeline/$', 'timeline', name='classical-timeline'),
    url(r'^timeline/data$', 'timeline_data', name='classical-timeline-data'),

    url(r'^artist/timeline/(?P<slug>[^/]+)$', 'artist_timeline', name='classical-artist-timeline'),
    url(r'^artist/timeline/(?P<slug>[^/]+)/data$', 'artist_timeline_data', name='classical-artist-timeline-data'),

    url(r'^artist/(?P<slug>[^/]+)$', 'artist', name='classical-artist'),
    url(r'^artist/(?P<artist_slug>[^/]+)/(?P<slug>[^/]+)$', 'work', name='classical-work'),
    url(r'^ensemble/(?P<slug>[^/]+)$', 'ensemble', name='classical-ensemble'),

    url(r'^play/recording/(?P<recording_id>\d+).m3u$', 'play_recording', name='classical-play-recording'),
)
