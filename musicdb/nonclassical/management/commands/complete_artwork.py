from django.core.management.base import BaseCommand

from musicdb.utils.urls import google_image_search

from musicdb.nonclassical.models import Album

class Command(BaseCommand):
    def handle(self, *files, **options):
        for album in Album.objects.filter(cover=''):
            print
            print "%s - %s" % (album.artist.long_name(), album)
            print google_image_search("%s %s" % (album.artist.long_name(), album))

            url = raw_input("Image URL: ")

            if url:
                album.set_artwork_from_url(url)
