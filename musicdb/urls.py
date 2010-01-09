from django.conf.urls.defaults import *

from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'musicdb.views.index', name='home'),

    url(r'^classical/', include('musicdb.classical.urls')),
    url(r'^albums/', include('musicdb.nonclassical.urls')),
    url(r'^common/', include('musicdb.common.urls')),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)', admin.site.root),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url('^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': 'media',
        }),
        url('^site_media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': 'site_media',
        }),
    )
