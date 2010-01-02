import os
import shutil

from django.conf import settings
from django.core.management.base import make_option

from musicdb.utils.urls import google_search
from musicdb.utils.commands import AddMusicFilesCommand
from musicdb.utils.progress import progress

from musicdb.common.models import File, MusicFile
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

            input = raw_input('[Y] or 1-%d to edit track name: ' % len(files))

            try:
                filename = files.keys()[int(input) - 1]

                files[filename] = self.prompt_new_name(files[filename])

            except (ValueError, KeyError):
                if input.upper() in ('', 'Y'):
                    break

        for trackname in files.values():
            assert trackname.strip()

        print "Creating CD..."
        cd = album.cds.create(num=album.cds.count() + 1)

        try:
            print "Copying tracks..."

            music_files = []
            for idx, (filename, trackname) in enumerate(progress(files.iteritems(), len(files))):
                extension = os.path.splitext(filename)[1][1:]

                file_ = File.objects.create_from_path(
                    src=filename,
                    location='albums/%d/%.2d.%s' % (
                        cd.pk,
                        idx + 1,
                        extension.lower() or 'mp3',
                    ),
                )

                music_file = MusicFile.objects.create(
                    file=file_,
                    rev_model='track',
                )

                music_files.append(music_file)

                cd.tracks.create(
                    num=idx + 1,
                    title=trackname,
                    music_file=music_file,
                )

            print "Tagging tracks..."
            for music_file in progress(music_files):
                music_file.tag()

        except:
            path = os.path.join(
                settings.MEDIA_LOCATION_RW,
                'albums', '%s' % cd.pk
            )

            print "Caught exception; cleaning up %r" % path
            shutil.rmtree(path)
            raise

        print "Saving to database..."
