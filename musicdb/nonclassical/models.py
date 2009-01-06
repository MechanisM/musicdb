from django.db import models

from musicdb.common.models import AbstractArtist, Nationality

from musicdb.fields import MySlugField, FirstLetterField, DirNameField

"""
Non-classical models.
"""

__all__ = ('Artist', 'Album', 'CD', 'Track', 'Performance')

class Artist(AbstractArtist):
    name = models.CharField(max_length=250)

    is_solo_artist = models.BooleanField(default=False)

    nationality = models.ForeignKey(
        Nationality, blank=True, null=True,
        related_name='nonclassical_artists',
    )

    name_first = FirstLetterField('name')
    dir_name = DirNameField('name')

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('nonclassical-artist', (self.slug,))

    def long_name(self):
        if self.is_solo_artist:
            try:
                last, first = self.name.split(', ', 1)
                return "%s %s" % (first, last)
            except ValueError:
                return self.name
        return self.name
    slug_name = long_name

    def albums(self):
        return Album.objects.filter(cds__tracks__performers__artist=self) \
            .distinct()

class Album(models.Model):
    title = models.CharField(max_length=200)
    year = models.IntegerField(blank=True, default=0)

    slug = MySlugField('title')
    dir_name = DirNameField('get_dir_name')

    class Meta:
        ordering = ('year', 'title')

    def __unicode__(self):
        if self.year:
            return u"%s (%d)" % (self.title, self.year)
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('nonclassical-album', (self.first_artist().slug, self.slug))

    def first_artist(self):
        return self.cds.all()[0].tracks.all()[0].performers.all()[0].artist

    def get_dir_name(self):
        if self.year:
            return "%d %s" % (self.year, self.title)
        return self.title

class CD(models.Model):
    album = models.ForeignKey(Album, related_name='cds')
    num = models.IntegerField()

    class Meta:
        ordering = ('num',)
        unique_together = ('album', 'num')

    def __unicode__(self):
        return u"CD %d of %d from %s" % \
            (self.num, self.album.cds.count(), self.album)

class Track(models.Model):
    title = models.CharField(max_length=250)
    cd = models.ForeignKey(CD, related_name='tracks')
    num = models.IntegerField()

    dir_name = DirNameField('get_dir_name')

    class Meta:
        ordering = ('num',)
        unique_together = ('cd', 'num')

    def __unicode__(self):
        return self.title

    def get_dir_name(self):
        return "%02d %s.mp3" % (self.num, self.title)

class Performance(models.Model):
    track = models.ForeignKey(Track, related_name='performers')
    num = models.IntegerField()
    artist = models.ForeignKey(Artist, related_name='performances')

    class Meta:
        unique_together = ('track', 'num')

    def __unicode__(self):
        return u"%s performing on %s" % (self.artist, self.track)
