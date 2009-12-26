from django.conf.urls.defaults import *

from .views import AddRecording

urlpatterns = patterns('musicdb.nonclassical_add.views',
    url(r'^$', AddRecording(), name='non-classical-add-recording'),
    url(r'^done/(?P<album_id>\d+)$', 'done', name='non-classical-add-recording-done'),
)
