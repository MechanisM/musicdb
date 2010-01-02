import os
import sys
import glob
import readline

from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from django.utils.datastructures import SortedDict

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

    def prompt_new_name(self, old_name):
        readline.add_history(old_name)

        return raw_input('New name [%s] (press up): ' % old_name) or old_name

    def prompt_year(self, name):
        readline.set_completer(None)
        while 1:
            try:
                input = raw_input('%s: ' % name)
                if not input:
                    return None

                year = int(input)

                if year < 1900:
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
