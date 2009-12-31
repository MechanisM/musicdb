from django.db import models

class ArtistManager(models.Manager):
    def composers(self):
        return self.filter(works__isnull=False).distinct()

    def artists(self):
        return self.filter(performances__isnull=False).distinct()
