import re
import urllib
import traceback

from django.core.management.base import BaseCommand

from musicdb.utils.progress import progress_qs

from musicdb.nonclassical.models import Album

re_image = re.compile(r'<a href="([^"]+)" title="View larger image"')

class Command(BaseCommand):
    def handle(self, *files, **options):
        qs = Album.objects.filter(cover='')
        orig_count = qs.count()

        for album in progress_qs(qs):
            try:
                self.handle_album(album)
            except:
                print "W: Caught exception finding artwork for %s (#%d)" % \
                    (album, album.pk)
                traceback.print_exc()

        qs = Album.objects.filter(cover='')
        print "Found %d cover(s)" % (orig_count - qs.count())

    def handle_album(self, album):
        both = "%s %s" % (album.artist.long_name(), album.title)

        for terms in (both, album.title):
            url = self.handle_terms(terms)

            if url:
                album.set_artwork_from_url(url)
                break

    def handle_terms(self, q):
        url = 'http://www.albumart.org/index.php?%s' % urllib.urlencode((
            ('srchkey', q.encode('utf8')),
            ('itempage', 1),
            ('newsearch', 1),
            ('searchindex', 'Music'),
        ))

        page = urllib.urlopen(url).read()

        m = re_image.search(page)
        if not m:
            return None

        return m.group(1)
