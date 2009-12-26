from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        from musicdb.classical.models import Work, Category
        from musicdb.classical.models import Category

        qs = Work.objects.exclude(category=None)
        print "Resetting %d Work objects with Category associations" % qs.count()
        qs.update(category=None)

        print "Deleting Category objects"
        Category.objects.all().delete()

        Category.load_bulk([
            {'data': {
                'name':         'Chamber music',
                'long_name':    'Chamber music',
            }, 'children': [
                {'data': {
                    'name':         'Solo instrument',
                    'long_name':    'Solo instrumental works',
                }, 'children': [
                    {'data': {
                        'name':         'Strings',
                        'long_name':    'Solo instrumental works for strings',
                    }, 'children': [
                        {'data': {
                            'name':         'Cello',
                            'long_name':    'Works for solo cello',
                        }},
                        {'data': {
                            'name':         'Viola',
                            'long_name':    'Works for solo viola',
                        }},
                        {'data': {
                            'name':         'Violin',
                            'long_name':    'Works for solo violin',
                        }},
                    ]},
                    {'data': {
                        'name':             'Piano',
                        'long_name':        'Works for solo piano',
                    }},
                ]},
                {'data': {
                    'name':         'With keyboard',
                    'long_name':    'Chamber music with keyboard',
                }, 'children': [
                    {'data': {
                        'name':         'Violin and keyboard',
                        'long_name':    'Works for violin and keyboard',
                    }},
                    {'data': {
                        'name':         'Cello and keyboard',
                        'long_name':    'Works for cello and keyboard',
                    }},
                    {'data': {
                        'name':         'Flute and keyboard',
                        'long_name':    'Works for flute and keyboard',
                    }},
                    {'data': {
                        'name':         'Clarinet and keyboard',
                        'long_name':    'Works for clarinet and keyboard',
                    }},
                    {'data': {
                        'name':         'Trio sonatas',
                        'long_name':    'Trio sonatas',
                    }},
                    {'data': {
                        'name':         'Piano trios',
                        'long_name':    'Piano trios',
                    }},
                    {'data': {
                        'name':         'Piano quartets',
                        'long_name':    'Piano quartets',
                    }},
                    {'data': {
                        'name':         'Piano quintets',
                        'long_name':    'Piano quintets',
                    }},
                ]},
                {'data': {
                    'name':         'Strings',
                    'long_name':    'Chamber music for strings',
                }, 'children': [
                    {'data': {
                        'name':         'String trio',
                        'long_name':    'String trios',
                    }},
                    {'data': {
                        'name':         'String quartet',
                        'long_name':    'String quartets',
                    }},
                    {'data': {
                        'name':         'String quintet',
                        'long_name':    'String quintets',
                    }},
                    {'data': {
                        'name':         'Cello quintet',
                        'long_name':    'Cello quintets',
                    }},
                    {'data': {
                        'name':         'String sextet',
                        'long_name':    'String sextets',
                    }},
                ]},
            ]},
            {'data': {
                'name':         'Orchestral music',
                'long_name':    'Orchestral music',
            }, 'children': [
                {'data': {
                    'name':         'Ballet',
                    'long_name':    'Ballet music',
                }},
                {'data': {
                    'name':         'For string orchestra',
                    'long_name':    'Works for string orchestra',
                }},
                {'data': {
                    'name':         'With solo instrument(s)',
                    'long_name':    'Solo instrument(s) and orchestra',
                }, 'children': [
                    {'data': {
                        'name':         'Violin',
                        'long_name':    'Works for violin and orchestra',
                    }},
                    {'data': {
                        'name':         'Viola',
                        'long_name':    'Viola concertos',
                    }},
                    {'data': {
                        'name':         'Cello',
                        'long_name':    'Works for cello and orchestra',
                    }},
                    {'data': {
                        'name':         'Piano',
                        'long_name':    'Works for piano and orchestra',
                    }},
                    {'data': {
                        'name':         'Harpsichord',
                        'long_name':    'Works for harpsichord and orchestra',
                    }},
                    {'data': {
                        'name':         'Flute',
                        'long_name':    'Works for flute and orchestra',
                    }},
                    {'data': {
                        'name':         'Bassoon',
                        'long_name':    'Works for bassoon and orchestra',
                    }},
                    {'data': {
                        'name':         'Oboe',
                        'long_name':    'Works for oboe and orchestra',
                    }},
                    {'data': {
                        'name':         'Horn',
                        'long_name':    'Works for horn and orchestra',
                    }},
                    {'data': {
                        'name':         'Multiple instruments',
                        'long_name':    'Works for multiple instruments and orchestra',
                    }},
                ]},
                {'data': {
                    'name':         'Incidental music',
                    'long_name':    'Incidental music',
                }},
                {'data': {
                    'name':         'Overtures',
                    'long_name':    'Overtures',
                }},
                {'data': {
                    'name':         'Suite',
                    'long_name':    'Orchestral suites',
                }},
                {'data': {
                    'name':         'Symphonic poem',
                    'long_name':    'Symphonic poems',
                }},
                {'data': {
                    'name':         'Symphony',
                    'long_name':    'Symphonies',
                }},
            ]},
            {'data': {
                'name':         'Vocal music',
                'long_name':    'Vocal music',
            }},
            {'data': {
                'name':         'Opera',
                'long_name':    'Operas',
            }},
        ], None)

        def update(qs, category):
            print "Put %d work(s) into the %s/%s category" % (qs.count(), category, category.long_name)
            qs.update(category=category)

        for category in Category.objects.all():
            if category.get_descendant_count():
                continue
            update(
                Work.objects.filter(title__istartswith=category.name),
                category,
            )
            if category.name.endswith('s'):
                update(
                    Work.objects.filter(title__istartswith=category.name[:-1]),
                    category,
                )

        mapping_data = {
            'istartswith': (
                ('Concerto Grosso',      'Works for multiple instruments and orchestra'),
                ('Brandenburg',          'Works for multiple instruments and orchestra'),
                ('Sinfonia Concertante', 'Works for multiple instruments and orchestra'),
                ('and keyboard Concertata',    'Works for multiple instruments and orchestra'),
                ('Solo Violin ',         'Works for solo violin'),
                ('Prelude and Fugue for String Trio', 'String trios'),
                ('Piano and keyboard',         'Works for solo piano'),
                ('Motet: ',              'Vocal music'),
                (' for Cello and Piano', 'Works for Cello and keyboard'),
                (' for Violin and Continuo', 'Works for violin and keyboard'),
                #('and keyboard for Violin and Harpsichord', 'Violin and keyboard'),
                #('Trio and keyboard', 'Trio and keyboard'),
                #('Slavonic Dance', 'Orchestral music'),
                #('Orchestral Suite', 'Suite'),
                ('Cello sonata',        'Works for cello and keyboard'),
                ('Violin sonata',       'Works for violin and keyboard'),
                ('Clarinet sonata',     'Works for clarinet and keyboard'),
                ('Cello concerto',      'Works for cello and orchestra'),
                ('Violin concerto',     'Works for violin and orchestra'),
            ),
            'icontains': (
                (' for string trio',            'String trios'),
                (' for piano trio',             'Piano trios'),
                (' for solo cello',             'Works for solo cello'),
                (' for Violin and Orchestra',   'Works for violin and orchestra'),
                (' for Piano and Orchestra',    'Works for piano and orchestra'),
                (' for Cello and orchestra',    'Works for cello and orchestra'),
                #(' for Cello and Piano', 'Cello and keyboard'),
                #(' for Violin and Piano', 'Violin and keyboard'),
                #(' for Piano and Violin', 'Violin and keyboard'),
                #(' for Clarinet and Piano', 'Clarinet and keyboard'),
                #(' for Piano and Flute', 'Flute and keyboard'),
            ),
        }

        for filter, mappings in mapping_data.items():
            for k, v in mappings:
                kwargs = {
                    'title__%s' % filter: k,
                }
                try:
                    category = Category.objects.get(long_name=v)
                except Category.DoesNotExist:
                    print "E: Could not find category with long_name=%r" % v
                    raise
                update(Work.objects.filter(**kwargs), category)

        qs = Work.objects.exclude(category=None)
        print "%d/%d Work objects now have Category associations" % \
            (qs.count(), Work.objects.count())


