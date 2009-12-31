import os
import shutil
import readline

from progressbar import *

from django.db import transaction
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError, make_option
from django.utils.datastructures import SortedDict

from musicdb.utils.completion import QuerySetCompleter

from musicdb.common.models import File, MusicFile
from musicdb.nonclassical.models import Artist
from musicdb.nonclassical_add.utils import track_names_from_filenames

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-m', '--move', dest='move', default=False,
            action='store_true', help="move, not copy files into target"),
    )

    def handle(self, *files, **options):
        self.options = options

        tracknames = track_names_from_filenames(files)
        files = SortedDict(zip(files, tracknames))

        if not files:
            raise CommandError("Must specify at least one file")

        for filename in files:
            if os.path.isfile(filename):
                continue

            raise CommandError("%r is not a valid file" % filename)

        readline.parse_and_bind("tab: complete")

        try:
            self.handle_files(files)
        except KeyboardInterrupt:
            pass

    @transaction.commit_on_success
    def handle_files(self, files):
        artist_name = self.prompt_string('Artist', Artist.objects.all(), 'name')

        artist, created = Artist.objects.get_or_create(name=artist_name)
        if created and ', ' in artist_name:
            artist.is_solo_artist = True
            artist.save()
        print "%s artist %s" % (created and 'Created' or 'Using existing', artist)

        album_name = self.prompt_string('Album name', artist.albums.all(), 'title')
        album, created = artist.albums.get_or_create(title=album_name)
        print "%s album %s" % (created and 'Created' or 'Using existing', album)

        album_year = created and self.get_album_year()
        if album_year:
            album.year = album_year
            album.save()

        while 1:
            print
            print "     %s - %s" % (artist_name, album_name),
            if album_year:
                print "(%d)" % album_year

            print

            pad_by = len(max(files.values(), key=len)) + 2
            for idx, (filename, trackname) in enumerate(files.iteritems()):
                print "% 3d) %s %s" % (
                    idx + 1,
                    trackname.ljust(pad_by),
                    os.path.basename(filename),
                )

            print

            input = raw_input('[Y] or 1-%d to edit track name: ' % len(files))

            try:
                filename = files.keys()[int(input) - 1]

                new_name = raw_input('New name [%s]: ' % files[filename])
                if new_name:
                    files[filename] = new_name

            except (ValueError, KeyError):
                if input.upper() in ('', 'Y'):
                    break

        for trackname in files.values():
            assert trackname.strip()

        print "Creating CD..."
        cd = album.cds.create(num=album.cds.count() + 1)

        try:
            print "%s tracks..." % (self.options['move'] and 'Moving' or 'Copying')

            music_files = []
            pbar = ProgressBar(maxval=len(files), widgets=(
                Percentage(), ' ', Bar(), ' ', ETA()
            )).start()
            for idx, (filename, trackname) in enumerate(files.iteritems()):
                extension = os.path.splitext(filename)[1][1:]

                file_ = File.objects.create_from_path(
                    src=filename,
                    location='mp3/albums/%d/%.2d.%s' % (
                        cd.pk,
                        idx + 1,
                        extension.lower() or 'mp3',
                    ),
                    move=self.options['move'],
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
                pbar.update(idx + 1)

            print "Tagging tracks..."
            pbar = ProgressBar(maxval=len(music_files), widgets=(
                Percentage(), ' ', Bar(), ' ', ETA()
            )).start()
            for idx, music_file in enumerate(music_files):
                music_file.tag()
                pbar.update(idx + 1)

            assert False

        except:
            path = os.path.join(
                settings.MEDIA_LOCATION_RW,
                'mp3', 'albums', '%s' % cd.pk
            )

            print "Caught exception; cleaning up %r" % path

            if self.options['move']:
                print "Moving files back (they may have been tagged though)"

                for idx, (filename, trackname) in enumerate(files.iteritems()):
                    extension = os.path.splitext(filename)[1][1:]

                    if os.path.exists(filename):
                        print "Not overwriting %r!" % filename
                    else:
                        shutil.move(
                            src=os.path.join(path, '%.2d.%s' % (
                                idx + 1,
                                extension.lower() or 'mp3',
                            )),
                            dst=filename,
                        )

            shutil.rmtree(path)

            raise

        print "Saving to database..."

    def prompt_string(self, name, qs, field):
        readline.set_completer(QuerySetCompleter(qs, field))
        readline.set_completer_delims('')

        while 1:
            input = raw_input('%s: ' % name)

            if not input:
                continue

            return input

    def get_album_year(self):
        readline.set_completer(None)
        while 1:
            try:
                input = raw_input('Album year: ')
                if not input:
                    return None

                year = int(input)

                if year < 1900:
                    continue

                return year
            except ValueError:
                pass
