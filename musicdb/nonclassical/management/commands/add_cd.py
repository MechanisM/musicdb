from django.core.management.base import make_option

from musicdb.utils.urls import google_search
from musicdb.utils.commands import AddMusicFilesCommand

from musicdb.nonclassical.models import Artist

class Command(AddMusicFilesCommand):
    option_list = AddMusicFilesCommand.option_list + (
        make_option('-a', '--artist', dest='artist', default='',
            action='store', help="artist name (optional)"),
        make_option('-b', '--album', dest='album', default='',
            action='store', help="album name (optional)"),
        make_option('-y', '--year', dest='year', default=None,
            action='store', help="album year (optional)"),
    )

    def handle_files(self, files):
        self.show_filenames(files)

        artist_name = self.options['artist']
        if not artist_name:
            artist_name = self.prompt_string('Artist', Artist.objects.all(), 'name')

        artist, created = Artist.objects.get_or_create(name=artist_name)
        if created and ', ' in artist_name:
            artist.is_solo_artist = True
            artist.save()
        print "%s artist %s" % (created and 'Created' or 'Using existing', artist)

        album_name = self.options['album']
        if not album_name:
            album_name = self.prompt_string('Album name', artist.albums.all(), 'title')

        album, created = artist.albums.get_or_create(title=album_name)
        print "%s album %s" % (created and 'Created' or 'Using existing', album)

        album_year = None
        if created:
            try:
                album_year = int(self.options['year'])
            except TypeError:
                print "Google this album: %s" % google_search('%s - %s' % (artist.long_name(), album.title))
                album_year = self.prompt_year('Album year')
            if album_year:
                album.year = album_year
                album.save()
        album_year = album.year

        while 1:
            print
            print "     %s - %s" % (artist_name, album_name),
            if album_year:
                print "(%d)" % album_year

            print

            self.show_filenames(files)

            if self.edit_track(files):
                break

        for trackname in files.values():
            assert trackname.strip()

        print "Creating CD..."
        cd = album.cds.create(num=album.cds.count() + 1)

        self.copy_and_tag(files, 'albums/%d' % cd.pk, 'track', cd.tracks)

        print "Saving to database..."
