from django.db import models

from django.db.models.aggregates import Count

class ArtistManager(models.Manager):
    def composers(self):
        return self.filter(works__isnull=False).distinct()

    def artists(self):
        return self.filter(performances__isnull=False).distinct()

    def by_num_works(self):
        return self.composers().annotate(
            num_works=Count('works'),
        ).order_by('-num_works')

class WorkManager(models.Manager):
    def by_num_recordings(self):
        return self.annotate(
            num_recordings=Count('recordings')
        ).order_by('-num_recordings')
