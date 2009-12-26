from django.contrib import admin

from musicdb.common import models

admin.site.register(models.Nationality)
admin.site.register(models.File)

class MusicFileAdmin(admin.ModelAdmin):
    raw_id_fields = ('file',)
admin.site.register(models.MusicFile, MusicFileAdmin)
