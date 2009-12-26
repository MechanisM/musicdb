from django.conf.urls.defaults import *

from .views import AddRecording

urlpatterns = patterns('musicdb.classical_add.views',
    url(r'^$', AddRecording(), name='classical-add-recording'),
    url(r'^add_work$', 'add_work', name='classical-add-work'),
    url(r'^add_artist$', 'add_artist', name='classical-add-artist'),
    url(r'^add_ensemble$', 'add_ensemble', name='classical-add-ensemble'),
    url(r'^add_instrument$', 'add_instrument', name='classical-add-instrument'),
    url(r'^done/(?P<recording_id>\d+)$', 'done', name='classical-add-recording-done'),
)
