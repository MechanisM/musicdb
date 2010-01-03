from musicdb.utils.commands import AddMusicFilesCommand

from musicdb.classical.models import Artist

"""
TODO

 - Work selection/creation
 - Ensemble/artist/instrument selection

"""

class Command(AddMusicFilesCommand):
    def handle_files(self, files):
        self.show_filenames(files)

        if False:
            composer = self.get_composer()
            work = self.get_work(composer)
        else:
            composer = Artist.objects.get(surname='beethoven')
            work = composer.works.get(slug='seven-variations-on-god-save-the-king-woo-78-in-c')

        recording = work.recordings.create(
            year=self.prompt_year('Recorded'),
        )

        self.confirm_movement_titles(recording, files)

        self.copy_and_tag(
            files,
            'classical/%d' % recording.pk,
            'movement',
            recording.movements,
        )

    def get_composer(self):
        composer_surname = self.prompt_string(
            'Composer surname',
            Artist.objects.all(),
            'surname',
        )
        composer_forenames = self.prompt_string(
            'Composer forenames',
            Artist.objects.filter(surname=composer_surname),
            'forenames',
        )

        artist, created = Artist.objects.get_or_create(
            surname=composer_surname, forenames=composer_forenames,
        )

        if created:
            prompt = lambda title: self.prompt_year(title, low=1300, high=2010)
            artist.born = prompt('Born')
            artist.died = prompt('Died')
            artist.save()

        print "I: %s artist %s" % (created and 'Created' or 'Using existing', artist)

        return artist

    def get_work(self, composer):
        work_slug = self.prompt_string(
            'Work slug', composer.works.all(), 'slug',
        )

        return composer.works.get(slug=work_slug)

    def confirm_movement_titles(self, recording, files):
        while True:
            print "%s - %s" % (recording.work.composer.long_name(), recording)

            self.show_filenames(files)
            if self.edit_track(files):
                break
