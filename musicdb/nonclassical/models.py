import os
import urllib

from mutagen import mp3, easyid3, File as MutagenFile

from django.db import models
from django.conf import settings
from django.core.files import File as DjangoFile
from django.db.models.aggregates import Sum

from musicdb.common.models import AbstractArtist, Nationality, MusicFile, File

from musicdb.db.mixins import NextPreviousMixin
from musicdb.db.fields import MySlugField, FirstLetterField, DirNameField
from musicdb.db.std_image.fields import StdImageField

from .managers import AlbumManager, TrackManager

"""
Non-classical models.
"""

__all__ = ('Artist', 'Album', 'CD', 'Track')

class Artist(AbstractArtist, NextPreviousMixin):
    name = models.CharField(max_length=250)

    is_solo_artist = models.BooleanField(
        'Artist represents a single person',
        default=False,
    )

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

class Album(models.Model, NextPreviousMixin):
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, related_name='albums')
    year = models.IntegerField(blank=True, null=True)

    cover = StdImageField(upload_to='album_covers', size=(300, 300), thumbnail_size=(125, 125), blank=True)

    slug = MySlugField('title')
    dir_name = DirNameField('get_dir_name')

    objects = AlbumManager()

    class Meta:
        ordering = ('year', 'title')

    def __unicode__(self):
        if self.year:
            return u"%s (%d)" % (self.title, self.year)
        return self.title

    def delete(self, *args, **kwargs):
        for track in self.get_tracks():
            track.delete()

        super(Album, self).delete(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('nonclassical-album', (self.artist.slug, self.slug))

    def get_dir_name(self):
        if self.year:
            return "%d %s" % (self.year, self.title)
        return self.title

    def get_tracks(self):
        return MusicFile.objects.filter(track__cd__album=self). \
            order_by('track__cd', 'track')

    def get_nonclassical_tracks(self):
        return Track.objects.filter(cd__album=self). \
            order_by('cd__num', 'track')

    def total_duration(self):
        return self.get_tracks().aggregate(Sum('length')).values()[0] or 0

    def next(self):
        return super(Album, self).next(artist=self.artist)

    def previous(self):
        return super(Album, self).previous(artist=self.artist)

    def set_artwork_from_url(self, url):
        tempfile, headers = urllib.urlretrieve(url)
        try:
            self.cover = DjangoFile(open(tempfile))
            self.save()
        except:
            self.cover.delete()
        finally:
            try:
                os.unlink(tempfile)
            except:
                pass

class CD(models.Model):
    album = models.ForeignKey(Album, related_name='cds')
    num = models.IntegerField()

    class Meta:
        ordering = ('num',)
        unique_together = ('album', 'num')
        verbose_name_plural = 'CDs'

    def __unicode__(self):
        return u"CD %d of %d from %s" % \
            (self.num, self.album.cds.count(), self.album)

    def get_tracks(self):
        return MusicFile.objects.filter(track__cd=self).order_by('track')

    def total_duration(self):
        return self.get_tracks().aggregate(Sum('length')).values()[0] or 0

class Track(models.Model):
    title = models.CharField(max_length=250)
    cd = models.ForeignKey(CD, related_name='tracks')
    num = models.IntegerField()
    music_file = models.OneToOneField(MusicFile, related_name='track')

    dir_name = DirNameField('get_dir_name')

    objects = TrackManager()

    class Meta:
        ordering = ('num',)
        unique_together = ('cd', 'num')

    def __unicode__(self):
        return self.title

    def get_dir_name(self):
        return "%02d %s.mp3" % (self.num, self.title)

    def metadata(self):
        album = self.cd.album
        return {
            'title': self.title,
            'album': unicode(album.title),
            'artist': unicode(album.artist.long_name()),
            'tracknumber': str(self.num),
            'date': str(album.year) or '',
        }

    @classmethod
    def quick_create(cls, abspath, cd, track_title, track_num):
        audio = MutagenFile(abspath)

        if isinstance(audio, mp3.MP3):
            extension = 'mp3'

        location = os.path.join(
            'albums',
            '%d' % cd.id,
            '%.2d.%s' % (track_num, extension),
        )

        file = File.create_from_path(abspath, location)

        music_file = MusicFile.objects.create(
            file=file,
            rev_model='track',
        )

        return cls.objects.create(
            cd=cd,
            num=track_num,
            title=track_title,
            music_file=music_file,
        )
