import os

from django.conf import settings
from django.http import HttpResponse
from django.utils import simplejson

class M3UResponse(HttpResponse):
    def __init__(self, tracks):
        prefix = settings.MEDIA_LOCATION

        content = '#EXTM3U\n'
        for track in tracks:
            content += '#EXTINF:%d,\n%s\n' % (
                track.length,
                os.path.join(prefix, track.file.location),
            )
        super(M3UResponse, self).__init__(content, mimetype='audio/x-mpegurl')
        self['Content-Disposition'] = 'attachment; filename=playlist.m3u'

class JSONResponse(HttpResponse):
    def __init__(self, data):
        super(JSONResponse, self).__init__(
            simplejson.dumps(data),
            mimetype='application/json',
        )
