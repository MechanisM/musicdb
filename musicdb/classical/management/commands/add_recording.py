import readline

from django.db.models import Count
from django.db.models.expressions import F

from musicdb.utils.commands import AddMusicFilesCommand
from musicdb.utils.completion import Completer

from musicdb.classical.models import Artist, Instrument, ArtistPerformance, \
    EnsemblePerformance, Ensemble, Performance, Key, Recording, Catalogue

"""
TODO

 - Work catalogue selection / creation
 - Re-using previous recording movement names
 - Add 'change' instrument to performer selection
"""

class Command(AddMusicFilesCommand):
    CAPITALISE_TRACK_NAMES = False

    def handle_files(self, files):
        self.show_filenames(files)

        if raw_input('Re-use last recording info? [Y] ').strip().lower() in ('y', ''):
            prev = Recording.objects.order_by('-pk')[0]
            composer = prev.work.composer

            print u"I: Using %s - %s (%s) as basis" % (
                prev.work.composer.short_name(),
                prev.work,
                prev.short_name(),
            )
        else:
            composer = self.get_artist('Composer')
            prev = None

        work = self.get_work(composer)

        year = self.prompt_year(
            'Recorded',
            default=prev and prev.year,
        )
        recording = work.recordings.create(year=year)

        self.performances(prev, recording)

        if len(files) > 1:
            self.confirm_movement_titles(recording, files)

        self.copy_and_tag(
            files,
            'classical/%d' % recording.pk,
            'movement',
            recording.movements,
        )

    def get_artist(self, name, prompt_years=True):
        surname = self.prompt_string(
            '%s surname' % name,
            Artist.objects.all(),
            'surname',
        )

        qs = Artist.objects.filter(surname=surname)
        default = qs.count() == 1 and qs[0].forenames or ''
        forenames = self.prompt_string(
            '%s forenames' % name,
            qs,
            'forenames',
            default,
        )

        artist, created = Artist.objects.get_or_create(
            surname=surname, forenames=forenames,
        )

        if created and prompt_years:
            prompt = lambda title: self.prompt_year(title, low=1300, high=2010)
            artist.born = prompt('Born')
            artist.died = prompt('Died')
            artist.save()

        print "I: %s %s %s" % (created and 'Created' or 'Using existing', name.lower(), artist)

        return artist

    def get_work(self, composer):
        works = dict((unicode(x).strip().encode('utf8'), x) for x in composer.works.all())

        Completer(works.keys()).install()

        while True:
            work_name = raw_input('Work (<enter> for new): ')

            if not work_name:
                break

            try:
                work = works[work_name.strip()]
                print "I: Using existing work: %s" % work
                return work
            except KeyError:
                print "E: Unknown work %r" % work_name
                continue

        title = self.prompt_string('Title')

        keys = dict((unicode(x).strip().encode('utf8'), x) for x in Key.objects.all())
        Completer(keys.keys()).install()

        key = None
        while True:
            key_name = raw_input('Key [None]: ').strip()

            if not key_name:
                break

            try:
                key = keys[key_name.strip()]
                break
            except KeyError:
                print "E: Unknown key %r" % key_name
                continue

        nickname = self.prompt_string('Nickname/subtitle', default='')
        year = self.prompt_year('Composed', low=1300, high=2010)

        work = composer.works.create(
            title=title,
            key=key,
            nickname=nickname,
            year=year,
        )

        self.get_catalogues(work)

        print "I: Created new work: %s" % work

        return work

    def get_catalogues(self, work):
        while True:
            txt = self.prompt_string('Catalogue', default='')

            try:
                prefix, value = txt.split(' ', 1)

                try:
                    catalogue = work.composer.catalogues.get(
                        prefix__startswith=prefix,
                    )
                except Catalogue.DoesNotExist:
                    catalogue = work.composer.catalogues.create(
                        prefix=prefix,
                        num=work.composer.catalogues.count() + 1,
                    )
                    print "I: Created %s" % catalogue

                work_catalogue = work.catalogues.create(
                    value=value,
                    catalogue=catalogue,
                )

                print "I: Work is now: %s" % work

            except ValueError:
                if not txt:
                    work.save() # To update denormalised fields
                    break
                print "E: Expected something like 'Op. 127'"

    def performances(self, prev, recording):
        if prev:
            # Copy previous performances onto this one
            for perf in prev.performances.all():
                kwargs = {
                    'recording': recording,
                    'num': perf.num,
                }

                if perf.subclass == 'artist':
                    kwargs['artist'] = perf.get_subclass().artist
                    kwargs['instrument'] = perf.get_subclass().instrument
                    ArtistPerformance.objects.create(**kwargs)
                else:
                    kwargs['ensemble'] = perf.get_subclass().ensemble
                    EnsemblePerformance.objects.create(**kwargs)

        while True:
            print "Performers"
            qs = recording.performances.all()

            for p in qs:
                subclass = p.get_subclass()

                if p.subclass == 'artist':
                    print "% 3d) %s (%s)" % (
                        p.num,
                        subclass.artist.long_name(),
                        subclass.instrument.noun.lower(),
                    )
                else:
                    print "% 3d) %s" % (p.num, subclass.ensemble)

            print

            s = raw_input('Add [a]rtist or [e]nsemble, [d]elete entry, move entry [u]p: ')
            if not s:
                break

            if s.lower() == 'a':
                artist = self.get_artist('Performer', prompt_years=False)
                ArtistPerformance.objects.create(
                    artist=artist,
                    instrument=self.get_instrument(artist),
                    recording=recording,
                    num=qs.count() + 1,
                )
            elif s.lower() == 'e':
                ensemble = self.get_ensemble()
                EnsemblePerformance.objects.create(
                    ensemble=ensemble,
                    recording=recording,
                    num=qs.count() + 1,
                )
            elif s.lower() == 'd':
                try:
                    num = int(raw_input('# to delete: '))

                    if num < 1:
                        raise ValueError()

                    qs.get(num=num).delete()
                    qs.filter(num__gt=num).update(
                        num=F('num') - 1,
                    )

                except (ValueError, Performance.DoesNotExist):
                    print "E: Invalid number"

            elif s.lower() in 'u':
                try:
                    num = int(raw_input('# to move up: '))

                    if num <= 1 or num > qs.count():
                        raise ValueError()

                    qs.filter(num=num - 1).update(num=0)
                    qs.filter(num=num).update(num=num - 1)
                    qs.filter(num=0).update(num=num)

                except ValueError:
                    print "E: Invalid number"

    def get_ensemble(self):
        name = self.prompt_string(
            'Ensemble', Ensemble.objects.all(), 'name',
        )

        ensemble, created = Ensemble.objects.get_or_create(name=name)

        return ensemble

    def get_instrument(self, artist):
        try:
            instrument_id = artist.performances.values('instrument'). \
                annotate(count=Count('instrument')). \
                order_by('-count')[0]['instrument']

            default = Instrument.objects.get(pk=instrument_id).noun
        except IndexError:
            default = None

        noun = self.prompt_string(
            'Instrument', Instrument.objects.all(), 'noun', default,
        )

        try:
            return Instrument.objects.get(noun=noun)
        except Instrument.DoesNotExist:
            adjective = ''
            while not adjective:
                adjective = raw_input('Adjective [%s player]: ' % noun) or \
                    '%s player' % noun

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
