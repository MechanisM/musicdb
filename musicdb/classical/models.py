# -*- coding: utf-8 -*-

import re
import roman

from django.db import models

from treebeard.mp_tree import MP_Node as TreeNode

from musicdb.common.models import AbstractArtist, Nationality, MusicFile

from musicdb.db.mixins import Mergeable
from musicdb.db.fields import MySlugField, DenormalisedCharField, DirNameField

from .managers import ArtistManager

"""
Classical models.
"""

__all__ = ('Artist', 'Ensemble', 'Work', 'Catalogue', 'WorkCatalogue', \
    'Category', 'Instrument', 'Key', 'Recording', 'Movement', \
    'Performance', 'WorkRelationship')

class Artist(AbstractArtist):
    surname = models.CharField(max_length=100)
    forenames = models.CharField(max_length=100)

    original_surname = models.CharField(max_length=100, blank=True)
    original_forenames = models.CharField(max_length=100, blank=True)

    born = models.IntegerField(blank=True, null=True)
    died = models.IntegerField(blank=True, null=True)
    born_question = models.BooleanField(
        'Year of birth uncertain',
        default=False,
    )
    died_question = models.BooleanField(
        'Year of death uncertain',
        default=False,
    )

    nationality = models.ForeignKey(
        Nationality, blank=True, null=True, related_name='classical_artists',
    )

    dir_name = DirNameField('__unicode__')

    objects = ArtistManager()

    class Meta:
        ordering = ('surname', 'forenames', 'born')

    def __unicode__(self):
        if self.forenames:
            name = "%s, %s" % (self.surname, self.forenames)
        else:
            name = self.surname

        if self.born or self.died:
            name += " (%s)" % self.date_range()

        return name

    @models.permalink
    def get_absolute_url(self):
        return ('classical-artist', (self.slug,))

    def slug_name(self):
        if self.forenames:
            return "%s %s" % (self.forenames, self.surname)
        else:
            return self.surname
    short_name = slug_name

    def long_name(self):
        name = "%s %s" % (self.forenames, self.surname)

        if self.original_surname or self.original_forenames:
            name += " (%s %s)" % (self.original_forenames, self.original_surname)

        if self.born or self.died:
            name += " (%s)" % self.date_range()

        return name

    def date_range(self):
        born = ""
        if self.born:
            born = "%d%s" % (self.born, self.born_question and '?' or '')

        died = ""
        if self.died:
            died = "%d%s" % (self.died, self.died_question and '?' or '')

        return "%s-%s" % (born, died)

    def performances_by_composer(self):
        return self.performances.order_by(
            'recording__work__composer',
            'recording__work__sort_value',
        )

    def instruments(self):
        return Instrument.objects.filter(performances__artist=self).distinct()

    def biography(self):
        items = []

        if self.works.count():
            items.append('composer')

        items.extend(self.instruments().values_list('adjective', flat=True))

        if self.nationality:
            nationality = u"%s " % self.nationality.adjective
        else:
            nationality = ""

        if len(items) > 1:
            last = items.pop()
            res = "%s%s and %s" % (nationality, ", ".join(items), last)
        else:
            res = "%s%s" % (nationality, items[0])

        return res.capitalize()

    def dirty_tags(self):
        # Compositions
        MusicFile.objects.filter(
            movement__recording__work__composer=self,
        ).update(tags_dirty=True)

        # Performances
        MusicFile.objects.filter(
            movement__recording__performances__artistperformance__artist=self,
        ).update(tags_dirty=True)

class Ensemble(models.Model, Mergeable):
    name = models.CharField(max_length=150)
    nationality = models.ForeignKey(
        Nationality, blank=True, null=True, related_name='ensembles'
    )
    slug = MySlugField('name')

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('classical-ensemble', (self.slug,))

    def performances_by_composer(self):
        return self.performances.order_by(
            'recording__work__composer',
            'recording__work__sort_value',
        )

    def dirty_tags(self):
        MusicFile.objects.filter(
            movement__recording__performances__ensembleperformance__ensemble=self,
        ).update(tags_dirty=True)

class Work(models.Model, Mergeable):
    title = models.CharField(max_length=200)
    nickname = models.CharField(max_length=200, blank=True)
    composer = models.ForeignKey(Artist, related_name='works')

    year = models.IntegerField('Year of composition', blank=True, null=True)
    year_question = models.BooleanField(
        'Year of composition is uncertain',
        default=False,
    )

    key = models.ForeignKey('Key', null=True, blank=True, related_name='works')
    category = models.ForeignKey('Category', null=True, blank=True, related_name='works')

    slug = MySlugField('slug_name', filter='slug_filter')
    sort_value = DenormalisedCharField('get_sort_value')

    class Meta:
        ordering = ('sort_value',)

    def __unicode__(self):
        return self.pretty_title()

    @models.permalink
    def get_absolute_url(self):
        return ('classical-work', (self.composer.slug, self.slug))

    def pretty_title(self, show_year=True):
        extras = [
            ('key', u" in %s"),
            ('nickname', u" «%s»"),
        ]
        if show_year:
            extras.append(('year', " (%d)"))

        ret = self.title
        if self.catalogues.count():
            ret += u", %s" % ", ".join([str(x) for x in self.catalogues.all()])

        for attr, format in extras:
            if getattr(self, attr):
                ret += format % getattr(self, attr)

        return ret

    def slug_name(self):
        return self.pretty_title(show_year=False)
    short_name = slug_name

    def slug_filter(self):
        return type(self).objects.filter(composer=self.composer)

    def get_sort_value(self):
        val = ''

        def zeropad(match):
            return "%04d" % int(match.group(0))

        for cat in self.catalogues.all():
            val += "%02d%s" % (cat.catalogue.num, \
                re.sub('\d+', zeropad, cat.value))

        val += re.sub('\d+', zeropad, self.title)
        val += self.nickname

        return val

    def dirty_tags(self):
        MusicFile.objects.filter(movement__recording__work=self).update(tags_dirty=True)

class WorkRelationship(models.Model):
    source = models.ForeignKey(Work, related_name='source_relations')
    derived = models.ForeignKey(Work, related_name='derived_relations')
    nature = models.CharField(max_length=13)

    def __unicode__(self):
        return u"%s => %s (%s)" % (self.source, self.derived, self.nature)

    def source_nature(self):
        return {
            'revision': 'newer revision',
        }.get(self.nature, self.nature)

    def derived_nature(self):
        return {
            'revision': 'revision',
        }.get(self.nature, 'source')

class Catalogue(models.Model):
    prefix = models.CharField(max_length=10)
    artist = models.ForeignKey(Artist, related_name='catalogues')
    num = models.IntegerField('Priority')

    class Meta:
        ordering = ('num',)
        unique_together = (
            ('artist', 'num'),
            ('artist', 'prefix'),
        )

    def __unicode__(self):
        return "%s catalogue of %s" % (self.prefix, self.artist)

    def dirty_tags(self):
        MusicFile.objects.filter(
            movement__recording__work__artist=self.artist,
        ).update(tags_dirty=True)

class WorkCatalogue(models.Model):
    work = models.ForeignKey(Work, related_name='catalogues')
    catalogue = models.ForeignKey(Catalogue, related_name='works')
    value = models.CharField(max_length=10)

    class Meta:
        ordering = ('catalogue__num',)

    def __unicode__(self):
        return "%s %s" % (self.catalogue.prefix, self.value)

    def dirty_tags(self):
        MusicFile.objects.filter(
            movement__recording__work=self,
        ).update(tags_dirty=True)

class Category(TreeNode):
    name = models.CharField(max_length=100)
    long_name = models.CharField(max_length=100, unique=True)

    slug = MySlugField('long_name')

    class Meta:
        ordering = ('path',)
        verbose_name_plural = 'Categories'

    def __unicode__(self):
        return self.long_name

    @models.permalink
    def get_absolute_url(self):
        return ('classical-category', (self.slug,))

    def works_by_composer(self):
        return self.works.order_by('composer', 'sort_value')

class Instrument(models.Model):
    noun = models.CharField(
        max_length=100, help_text="For example, 'Cello'", unique=True
    )
    adjective = models.CharField(
        max_length=100, help_text="For example, 'Cellist'", unique=True
    )

    class Meta:
        ordering = ('noun',)

    def __unicode__(self):
        return self.noun

class Key(models.Model):
    name = models.CharField(max_length=13)
    minor = models.BooleanField(default=False)

    class Meta:
        ordering = ('name', 'minor')
        unique_together = (('name', 'minor'),)

    def __unicode__(self):
        #val = self.name.replace('-flat', u'♭').replace('-sharp', u'♯') # breaks slugs
        val = self.name

        if self.minor:
            return u"%s minor" % val

        return val

# Recording-specific

class Recording(models.Model):
    work = models.ForeignKey(Work, related_name='recordings')
    year = models.IntegerField(blank=True, null=True)

    slug = MySlugField('slug_name', filter='slug_filter')

    def __unicode__(self):
        ret = u"%s" % self.work
        if self.year:
            ret += u" (%d)" % self.year
        return ret

    def get_absolute_url(self):
        return "%s#%s" % (self.work.get_absolute_url(), self.slug)

    def short_name(self):
        return ", ".join([
            x.get_subclass().short_name() for x in self.performances.all()
        ])

    def slug_name(self):
        ret = unicode(self.short_name())
        if self.year:
            ret += " %d" % self.year
        return ret

    def slug_filter(self):
        return type(self).objects.filter(work=self.work)

    def get_tracks(self):
        return MusicFile.objects.filter(movement__recording=self).order_by('movement')

    def total_duration(self):
        return sum(self.get_tracks().values_list('length', flat=True))

    def dirty_tags(self):
        self.get_tracks().update(tags_dirty=True)

class Movement(models.Model):
    recording = models.ForeignKey(Recording, related_name='movements')
    title = models.CharField(max_length=300)
    music_file = models.OneToOneField(MusicFile, related_name='movement')
    section_title = models.CharField(max_length=200, blank=True)
    num = models.IntegerField()

    class Meta:
        ordering = ('num',)
        unique_together = ('recording', 'num')

    def __unicode__(self):
        return self.title

    def metadata(self):
        title = self.recording.work.pretty_title(show_year=False)
        if self.recording.movements.count() > 1:
            title += u' - %s. %s' % (roman.toRoman(self.num), self.title)
        title += u' (%s)' % self.recording.short_name()

        return {
            'title': title,
            'artist': unicode(self.recording.work.composer),
            'tracknumber': str(self.num),
            'genre': 'Classical',
            'date': str(self.recording.year) or '',
        }

    def dirty_tags(self):
        MusicFile.objects.filter(id=self.music_file).update(tags_dirty=True)

class Performance(models.Model):
    recording = models.ForeignKey(Recording, related_name='performances')
    num = models.IntegerField()
    subclass = models.CharField(max_length=8)

    class Meta:
        unique_together = ('recording', 'num')
        ordering = ('num',)

    def __unicode__(self):
        return u"%s" % self.get_subclass()

    def save(self, *args, **kwargs):
        created = not self.id
        if created:
            self.subclass = {
                'ArtistPerformance': 'artist',
                'EnsemblePerformance': 'ensemble',
            }[type(self).__name__]
        return super(Performance, self).save(*args, **kwargs)

    def get_subclass(self):
        return getattr(self, '%sperformance' % self.subclass)

class ArtistPerformance(Performance):
    artist = models.ForeignKey(Artist, related_name='performances')
    instrument = models.ForeignKey(Instrument, related_name='performances')

    class Meta:
        ordering = ('instrument',)

    def __unicode__(self):
        return u"%s performing the %s on %s" % \
            (self.artist, self.instrument.noun.lower(), self.recording)

    def short_name(self):
        return self.artist.surname

class EnsemblePerformance(Performance):
    ensemble = models.ForeignKey(
        Ensemble, related_name='performances',
    )

    def __unicode__(self):
        return u"%s performing on %s" % \
            (self.ensemble, self.recording)

    def short_name(self):
        return self.ensemble.name
