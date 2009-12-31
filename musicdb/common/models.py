import os

from mutagen import mp3, easyid3, File as MutagenFile

from django.db import models
from django.conf import settings

from musicdb.db.fields import MySlugField

from .managers import FileManager

"""
Common models.
"""

__all__ = ('AbstractArtist', 'Nationality', 'MusicFile')

class AbstractArtist(models.Model):
    slug = MySlugField('slug_name')
    url = models.CharField(max_length=200, blank=True)

    class Meta:
        abstract = True

class Nationality(models.Model):
    adjective = models.CharField("For example, 'English'", max_length=50)
    noun = models.CharField("For example, 'England'", max_length=50)

    class Meta:
        ordering = ('noun',)
        verbose_name_plural = 'Nationalities'

    def __unicode__(self):
        return self.adjective

class File(models.Model):
    location = models.CharField(unique=True, max_length=255)
    size = models.IntegerField('File size in bytes')

    objects = FileManager()

    def __unicode__(self):
        return "%s (%d bytes)" % (self.location, self.size)

    def save(self, *args, **kwargs):
        if not self.size:
            self.size = os.path.getsize(os.path.join(
                settings.MEDIA_LOCATION,
                self.location,
            ))
        super(File, self).save(*args, **kwargs)

class MusicFile(models.Model):
    file = models.OneToOneField(File)
    length = models.IntegerField('Duration in seconds')
    rev_model = models.CharField(max_length=8) # track, movement
    type = models.CharField(max_length=4) # mp3, flac
    tags_dirty = models.NullBooleanField(
       'File metadata is out of sync',
        default=True,
    )

    def __unicode__(self):
        return 'Length %ds (from %s)' % (self.length, self.file)

    def save(self, *args, **kwargs):
        if not self.length:
            filename = os.path.join(settings.MEDIA_LOCATION, self.file.location)
            audio = MutagenFile(filename)

            if isinstance(audio, mp3.MP3):
                self.type = 'mp3'
            else:
                assert False, "FIXME"

            self.length = int(audio.info.length)

        super(MusicFile, self).save(*args, **kwargs)

    def get_parent_instance(self):
        return getattr(self, self.rev_model)

    def tag(self):
        try:
            data = self.get_parent_instance().metadata()
            filename = os.path.join(settings.MEDIA_LOCATION_RW, self.file.location)
            audio = MutagenFile(filename)
            audio.delete()
            if isinstance(audio, mp3.MP3):
                audio.tags = easyid3.EasyID3()
            audio.update(data)
            audio.save()
        except:
            self.tags_dirty = None
            self.save()
            raise
        finally:
            self.tags_dirty = False
            self.save()
