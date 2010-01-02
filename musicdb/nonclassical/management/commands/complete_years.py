from django.core.management.base import BaseCommand

from musicdb.utils.urls import google_search

from musicdb.nonclassical.models import Album

class Command(BaseCommand):
    def handle(self, *files, **options):
        for album in Album.objects.filter(year=0):
            print
            print "%s - %s" % (album.artist.long_name(), album)
            print google_search("%s %s" % (album.artist.long_name(), album))

            year = raw_input("Year: ")

            try:
                album.year = int(year)

                if album.year < 1900 or album.year > 2020:
                    raise ValueError

                album.save()
            except ValueError:
                pass
