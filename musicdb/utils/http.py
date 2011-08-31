import os

from lxml import etree

from django.conf import settings
from django.http import HttpResponse
from django.utils import simplejson

class M3UResponse(HttpResponse):
    def __init__(self, tracks):
        prefix = settings.MEDIA_LOCATION
        prefix = 'http://musicdb.chris-lamb.co.uk/share/chou6OhS'

        content = '#EXTM3U\n'
        for track in tracks:
            content += '#EXTINF:%d,\n%s\n' % (
                track.length,
                os.path.join(prefix, track.file.location),
            )
        super(M3UResponse, self).__init__(content, mimetype='audio/x-mpegurl')
        self['Content-Disposition'] = 'attachment; filename=playlist.m3u'

class XSPFResponse(HttpResponse):
    def __init__(self, tracks):
        prefix = settings.MEDIA_LOCATION
        prefix = 'http://musicdb.chris-lamb.co.uk/share/chou6OhS'

        NSMAP = {
            None: 'http://xspf.org/ns/0/',
        }

        playlist = etree.Element('playlist', nsmap=NSMAP, attrib={
            'version': '1',
        })

        track_list = etree.SubElement(playlist, 'trackList')

        for track in tracks:
            elem = etree.SubElement(track_list, 'track')

            title = etree.SubElement(elem, 'title')
            title.text = track.get_parent_instance().title

            duration = etree.SubElement(elem, 'duration')
            duration.text = unicode(track.length * 1000)

            location = etree.SubElement(elem, 'location')
            location.text = os.path.join(prefix, track.file.location)

        super(XSPFResponse, self).__init__(
            etree.tounicode(playlist),
            mimetype='application/xspf+xml',
        )

        self['Content-Disposition'] = 'attachment; filename=playlist.xspf'

class JSONResponse(HttpResponse):
    def __init__(self, data):
        super(JSONResponse, self).__init__(
            simplejson.dumps(data),
            mimetype='application/json',
        )
