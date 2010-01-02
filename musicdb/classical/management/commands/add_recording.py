from musicdb.utils.commands import AddMusicFilesCommand

from musicdb.nonclassical.models import Artist

class Command(AddMusicFilesCommand):
    def handle_files(self, files):
        self.show_filenames(files)
