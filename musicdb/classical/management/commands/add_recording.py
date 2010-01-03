from musicdb.utils.commands import AddMusicFilesCommand

from musicdb.classical.models import Artist, Instrument, ArtistPerformance

"""
TODO

 - Work selection/creation
 - Ensemble/artist/instrument selection

"""

class Command(AddMusicFilesCommand):
    def handle_files(self, files):
        self.show_filenames(files)

        if False:
            composer = self.get_artist('Composer')
            work = self.get_work(composer)
        else:
            composer = Artist.objects.get(surname='beethoven')
            work = composer.works.get(slug='seven-variations-on-god-save-the-king-woo-78-in-c')

        recording = work.recordings.create(
            year=self.prompt_year('Recorded'),
        )

        self.performances(recording)

        self.confirm_movement_titles(recording, files)

        self.copy_and_tag(
            files,
            'classical/%d' % recording.pk,
            'movement',
            recording.movements,
        )

    def get_artist(self, name):
        surname = self.prompt_string(
            '%s surname' % name,
            Artist.objects.all(),
            'surname',
        )
        forenames = self.prompt_string(
            '%s forenames' % name,
            Artist.objects.filter(surname=surname),
            'forenames',
        )

        artist, created = Artist.objects.get_or_create(
            surname=surname, forenames=forenames,
        )

        if created:
            prompt = lambda title: self.prompt_year(title, low=1300, high=2010)
            artist.born = prompt('Born')
            artist.died = prompt('Died')
            artist.save()

        print "I: %s %s %s" % (created and 'Created' or 'Using existing', name.lower(), artist)

        return artist

    def get_work(self, composer):
        work_slug = self.prompt_string(
            'Work slug', composer.works.all(), 'slug',
        )

        return composer.works.get(slug=work_slug)

    def performances(self, recording):
        while True:
            print "Performers"

            for p in recording.performances.all():
                subclass = p.get_subclass()

                if p.subclass == 'artist':
                    print "% 3d) %s (%s)" % (
                        p.num,
                        subclass.artist.long_name(),
                        subclass.instrument.noun.lower(),
                    )
                else:
                    assert False

            print

            s = raw_input('Add [a]rtist or [e]nsemble: ')
            if not s:
                break

            if s.lower() == 'a':
                artist = self.get_artist('Performer')
                ArtistPerformance.objects.create(
                    artist=artist,
                    instrument=self.get_instrument(artist),
                    recording=recording,
                    num=recording.performances.count() + 1,
                )

    def get_instrument(self, artist):
        default = None
        artist_instruments = list(artist.instruments())
        if len(artist_instruments) == 1:
            default = artist_instruments[0].noun

        noun = self.prompt_string(
            'Instrument', Instrument.objects.all(), 'noun', default,
        )

        try:
            return Instrument.objects.get(noun=noun)
        except Instrument.DoesNotExist:
            adjective = ''
            while not adjective:
                adjective = raw_input('Adjective for "%s player": ' % noun)

            return Instrument.objects.create(
                noun=noun,
                adjective=adjective,
            )

    def confirm_movement_titles(self, recording, files):
        while True:
            print "%s - %s" % (recording.work.composer.long_name(), recording)

            self.show_filenames(files)
            if self.edit_track(files):
                break
