from django.core.management.base import NoArgsCommand

from musicdb.classical.models import *

class Command(NoArgsCommand):
    def handle_noargs(self, **options):

        work_pairs = (
            ('felix-mendelssohn', ('string-quartet-in-e-flat', 'string-quartet-in-e-flat-1')),
            ('ludvig-van-beethoven', ('piano-trio-in-e-flat-triosatz', 'piano-trio-in-e-flat-triosatz-1')),
            ('fryderyk-chopin', ('ballade-no-4-op-52-in-f-minor', 'ballade-no-4-op-52-in-f-minor-1')),
        )

        for a, (b, c) in work_pairs:
            try:
                Work.objects.get(composer__slug=a, slug=b).merge_from(
                    Work.objects.get(composer__slug=a, slug=c)
                )
            except Work.DoesNotExist:
                print "W: Skipping", a, b, c

        ensemble_pairs = (
            ('chamber-orchestra-of-europe', 'chamber-orchestra-of-europe-1'),
            ('orquestra-sinfonica-haydn-de-bolzano-e-trento', 'orquestra-sinfonica-haydn-de-bolzano-e-trento-1'),
            ('i-solisti-veneti', 'i-solisti-veneti-1'),
            ('london-symphony-orchestra', 'london-symphony-orchestra-principals'),
            ('vienna-philharmonic-orchestra', 'wiener-philharmoniker'),
        )

        for a, b in ensemble_pairs:
            try:
                Ensemble.objects.get(slug=a).merge_from(Ensemble.objects.get(slug=b))
            except Ensemble.DoesNotExist:
                print "W: Skipping", a, b

        relationships = {
            'arrangement': (
                ('orchesographie', 'capriol-suite-for-string-orchestra'),
            ),
            'revision': (
                ('brandenburg-concerto-no-5-early-version-bwv-1050a-in-d', 'brandenburg-concerto-no-5-bwv-1050-in-d'),
                ('brandenburg-concerto-no-1-early-version-bwv-1046a-in-f', 'brandenburg-concerto-no-1-bwv-1046-in-f'),
            ),
            'variations': (
                ('twelve-variations-on-ah-vous-dirai-je-maman-k-265-in-c', 'romantic-piece-op-18'),
            ),
            'transcription': (
                ('brandenburg-concerto-no-4-bwv-1049-in-g', 'concerto-for-harpsichord-and-two-recorders-transcription-of-brandenburg-concerto-no-4-bwv-1057'),
                ('violin-concerto-bwv-1041-in-a-minor', 'harpsichord-concerto-bwv-1058r-in-g-minor'),
                ('violin-concerto-bwv-1042-in-e', 'harpsichord-concerto-bwv-1054-in-d'),
                ('concerto-for-oboe-and-violin-bwv-1060r-in-g-minor', 'concerto-for-two-harpsichords-bwv-1060-in-c-minor'),
                ('double-violin-concerto-bwv-1043-in-d-minor', 'concerto-for-two-harpsichords-bwv-1062-in-c-minor'),
                ('concerto-for-three-violins-bwv-1064r-in-d', 'concerto-for-three-harpsichords-bwv-1064-in-c'),
                ('concerto-for-four-violins-op-3-no-10-rv-580-in-b-minor', 'concerto-for-three-harpsichords-bwv-1064-in-c'),
                ('concerto-for-oboe-damore-bwv-1055r-in-a', 'harpsichord-concerto-bwv-1055-in-a'),
            )
        }

        for nature, data in relationships.items():
            for x, y in data:
                WorkRelationship.objects.create(
                    source=Work.objects.get(slug=x),
                    derived=Work.objects.get(slug=y),
                    nature=nature,
                )

        to_delete = ()

        for klass, pks in to_delete:
            for pk in pks:
                try:
                    klass.objects.get(pk=pk).delete()
                except klass.DoesNotExist:
                    print "W: Skipping deletion of", klass, pk
