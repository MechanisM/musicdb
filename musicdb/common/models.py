from django.db import models

from musicdb.fields import MySlugField

"""
Common models.
"""

__all__ = ('AbstractArtist', 'Nationality')

class AbstractArtist(models.Model):
    slug = MySlugField('slug_name')
    url = models.CharField(max_length=200, blank=True)

    class Meta:
        abstract = True

class Nationality(models.Model):
    adjective = models.CharField(
        max_length=50, help_text="For example, 'English'"
    )
    noun = models.CharField(
        max_length=50, help_text="For example, 'England'"
    )

    class Meta:
        ordering = ('noun',)
        verbose_name_plural = 'Nationalities'

    def __unicode__(self):
        return self.adjective
