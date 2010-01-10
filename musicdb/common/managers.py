import os
import shutil

from django.db import models
from django.conf import settings

class FileManager(models.Manager):
    def create_from_path(self, src, location, move=False):
        abs_location = os.path.join(settings.MEDIA_LOCATION, location)

        try:
            os.makedirs(os.path.dirname(abs_location))
        except OSError:
            # Directory already exists
            pass

        op = (move and shutil.move or shutil.copyfile)

        op(src, abs_location)

        return self.create(location=location)
