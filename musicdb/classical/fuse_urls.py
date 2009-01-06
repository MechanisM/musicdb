from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
    url(r'^$', views.fuse_index),
    url(r'^/(?P<dir_name>[^/]+)$', views.fuse_artist),
)
