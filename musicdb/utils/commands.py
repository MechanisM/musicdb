import os
import sys
import glob
import shutil
import readline

from django.db import transaction
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.datastructures import SortedDict

from musicdb.common.models import File, MusicFile

from .progress import progress
from .completion import QuerySetCompleter
from .track_names import track_names_from_filenames

class AddMusicFilesCommand(BaseCommand):
    def handle(self, *files, **options):
        self.options = options

        # Expand if we have specified a directory
        if len(files) == 1 and os.path.isdir(files[0]):
            expanded = sorted(glob.glob(os.path.join(files[0], '*')))
            files = []

            for filename in expanded:
                if os.path.splitext(filename)[1].lower() in ('.flac', '.mp3'):
                    files.append(filename)

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
            self._handle_files(files)
        except KeyboardInterrupt:
            sys.exit(1)

    @transaction.commit_on_success
    def _handle_files(self, files):
        return self.handle_files(files)

    def prompt_string(self, name, qs, field):
        readline.set_completer(QuerySetCompleter(qs, field))
        readline.set_completer_delims('')

        while 1:
            input = raw_input('%s: ' % name)

            if not input:
                continue

            return input.decode('utf8')

    def edit_track(self, files):
        input = raw_input('[Y] or 1-%d to edit name: ' % len(files))

        try:
            filename = files.keys()[int(input) - 1]
            old_name = files[filename]

            readline.add_history(old_name)
            new_name = raw_input('New name [%s] (press up): ' % old_name)

            files[filename] = new_name or old_name
        except (ValueError, KeyError):
            if input.upper() in ('', 'Y'):
                return True

        return False

    def prompt_year(self, name, low=1900, high=2020):
        readline.set_completer(None)
        while 1:
            try:
                input = raw_input('%s: ' % name)
                if not input:
                    return None

                year = int(input)

                if year < low or year > high:
                    continue

                return year
            except ValueError:
                pass

    def show_filenames(self, files):
        pad_by = len(max(files.values(), key=len)) + 2
        for idx, (filename, trackname) in enumerate(files.iteritems()):
            print "% 3d) %s %s" % (
                idx + 1,
                trackname.ljust(pad_by),
                os.path.basename(filename),
            )
        print

    def copy_and_tag(self, files, target, rev_model, manager):
        try:
            print "Copying tracks..."

            music_files = []
            for idx, (filename, trackname) in enumerate(progress(files.iteritems(), len(files))):
                extension = os.path.splitext(filename)[1][1:]

                file_ = File.objects.create_from_path(
                    src=filename,
                    location='%s/%.2d.%s' % (
                        target,
                        idx + 1,
                        extension.lower() or 'mp3',
                    ),
                )

                music_file = MusicFile.objects.create(
                    file=file_,
                    rev_model=rev_model,
                )

                manager.create(
                    num=idx + 1,
                    title=trackname,
                    music_file=music_file,
                )

                music_files.append(music_file)

            print "Tagging tracks..."
            for music_file in progress(music_files):
                music_file.tag()

        except:
            path = os.path.join(settings.MEDIA_LOCATION_RW, target)

            print "Caught exception; cleaning up %r" % path
            shutil.rmtree(path)
            raise
