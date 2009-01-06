# -*- coding: utf-8 -*-

import re

from django.db import models
from treebeard.mp_tree import MP_Node as TreeNode

from musicdb.common.models import AbstractArtist, Nationality

from musicdb.fields import MySlugField, DenormalisedCharField, DirNameField

"""
Classical models.
"""

__all__ = ('Artist', 'Ensemble', 'Work', 'Catalogue', 'WorkCatalogue', \
    'Category', 'Instrument', 'Key', 'Recording', 'Movement', \
    'Performance')

class Artist(AbstractArtist):
    surname = models.CharField(max_length=100)
    forenames = models.CharField(max_length=100)

    original_surname = models.CharField(max_length=100, blank=True)
    original_forenames = models.CharField(max_length=100, blank=True)

    born = models.IntegerField(blank=True, default=0)
    died = models.IntegerField(blank=True, default=0)
    born_question = models.BooleanField(default=False)
    died_question = models.BooleanField(default=False)

    nationality = models.ForeignKey(
        Nationality, blank=True, null=True, related_name='classical_artists',
    )

    dir_name = DirNameField('__unicode__')

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

class Ensemble(models.Model):
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

class Work(models.Model):
    title = models.CharField(max_length=200)
    nickname = models.CharField(max_length=200, blank=True)
    composer = models.ForeignKey(Artist, related_name='works')

    year = models.IntegerField(blank=True, default=0)
    year_question = models.BooleanField(default=False)

    key = models.ForeignKey('Key', null=True, related_name='works')
    category = models.ForeignKey('Category', null=True, related_name='works')

    slug = MySlugField('slug_name', filter='slug_filter')
    sort_value = DenormalisedCharField('get_sort_value')

    class Meta:
        ordering = ('sort_value',)

    @models.permalink
    def get_absolute_url(self):
        return ('classical-work', (self.composer.slug, self.slug))

    def __unicode__(self, show_year=True):
        extras = [
            ('key', " in %s"),
            ('nickname', u" «%s»"),
        ]
        if show_year:
            extras.append(('year', " (%d)"))

        ret = self.title
        if self.catalogues.all():
            ret += ", %s" % ", ".join([str(x) for x in self.catalogues.all()])

        for attr, format in extras:
            if getattr(self, attr):
                ret += format % getattr(self, attr)

        return ret

    def slug_name(self):
        return self.__unicode__(show_year=False)
    short_name = slug_name

    def slug_filter(self):
        return self.__class__.objects.filter(composer=self.composer)

    def get_sort_value(self):
        val = ''

        def zeropad(match):
            return "%04d" % int(match.group(0))

        for cat in self.catalogues.all():
            val += "%02d%s" % (cat.catalogue.num, \
                re.sub('\d+', zeropad, cat.value))

        val += self.title
        val += self.nickname

        return val

class Catalogue(models.Model):
    prefix = models.CharField(max_length=10)
    artist = models.ForeignKey(Artist, related_name='catalogues')
    num = models.IntegerField()

    class Meta:
        ordering = ('num',)
        unique_together = (
            ('artist', 'num'),
            ('artist', 'prefix'),
        )

    def __unicode__(self):
        return "%s catalogue of %s" % (self.prefix, self.artist)

class WorkCatalogue(models.Model):
    work = models.ForeignKey(Work, related_name='catalogues')
    catalogue = models.ForeignKey(Catalogue, related_name='works')
    value = models.CharField(max_length=10)

    class Meta:
        ordering = ('value',)

    def __unicode__(self):
        return "%s %s" % (self.catalogue.prefix, self.value)

class Category(TreeNode):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

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
        if self.minor:
            return "%s minor" % self.name
        return self.name

# Recording-specific

class Recording(models.Model):
    work = models.ForeignKey(Work, related_name='recordings')
    year = models.IntegerField(blank=True, default=0)

    def __unicode__(self):
        ret = "%s" % self.work
        if self.year:
            ret += " (%d)" % self.year
        return ret

    def short_name(self):
        return ", ".join([
            x.get_subclass().short_name() for x in self.performances.all()
        ])

class Movement(models.Model):
    title = models.CharField(max_length=300)
    section_title = models.CharField(max_length=200, blank=True)
    recording = models.ForeignKey(Recording, related_name='movements')
    num = models.IntegerField()

    class Meta:
        ordering = ('num',)
        unique_together = ('recording', 'num')

    def __unicode__(self):
        return self.title

class Performance(models.Model):
    recording = models.ForeignKey(Recording, related_name='performances')
    num = models.IntegerField()
    subclass = models.CharField(max_length=8)

    class Meta:
        unique_together = ('recording', 'num')
        ordering = ('num',)

    def save(self, *args, **kwargs):
        self.subclass = {
            'ArtistPerformance': 'artist',
            'EnsemblePerformance': 'ensemble',
        }[type(self).__name__]
        return super(Performance, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"%s" % self.get_subclass()

    def get_subclass(self):
        return getattr(self, '%sperformance' % self.subclass)

class ArtistPerformance(Performance):
    artist = models.ForeignKey(Artist, related_name='performances')
    instrument = models.ForeignKey(Instrument)

    def __unicode__(self):
        return "%s performing the %s on %s" % \
            (self.artist, self.instrument.noun.lower(), self.recording)

    def short_name(self):
        return self.artist.surname

class EnsemblePerformance(Performance):
    ensemble = models.ForeignKey(
        Ensemble, related_name='performances',
    )

    def __unicode__(self):
        return "%s performing on %s" % \
            (self.ensemble, self.recording)

    def short_name(self):
        return self.ensemble.name
