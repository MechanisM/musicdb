from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
    url(r'^$', views.fuse_index, name='home'),
    url(r'^Classical', include('musicdb.classical.fuse_urls')),
    url(r'^Albums', include('musicdb.nonclassical.fuse_urls')),
)
