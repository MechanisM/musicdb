import re
import urllib

from django.core.files import File
from django.core.management.base import BaseCommand

from musicdb.utils.progress import progress_qs

from musicdb.nonclassical.models import Album

re_image = re.compile(r'<a href="([^"]+)" title="View larger image"')

class Command(BaseCommand):
    def handle(self, *files, **options):
        qs = Album.objects.filter(cover='')
        orig_count = qs.count()

        for album in progress_qs(qs):
            self.handle_album(album)

        qs = Album.objects.filter(cover='')
        print "Found %d cover(s)" % (orig_count - qs.count())

    def handle_album(self, album):
        both = "%s %s" % (album.artist.long_name(), album.title)

        for terms in (both, album.title):
            url = self.handle_terms(terms)

            if url:
                self.handle_image_url(album, url)
                break

    def handle_image_url(self, album, url):
        tempfile, headers = urllib.urlretrieve(url)
        try:
            album.cover = File(open(tempfile))
            album.save()
        finally:
            try:
                os.unlink(tempfile)
            except:
                pass

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
