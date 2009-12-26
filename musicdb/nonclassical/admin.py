from django.contrib import admin

from musicdb.nonclassical import models

class ArtistAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'is_solo_artist')}
        ),
        (None, {
            'fields': ('nationality',)}
        ),
    )
admin.site.register(models.Artist, ArtistAdmin)

class AlbumAdmin(admin.ModelAdmin):
    fields = ('title', 'artist', 'year', 'cover')
admin.site.register(models.Album, AlbumAdmin)

class CDAdmin(admin.ModelAdmin):
    fields = ('album', 'num')
admin.site.register(models.CD, CDAdmin)

class TrackAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('title', 'num')}
        ),
        (None, {
            'fields': ('cd',)}
        ),
    )
admin.site.register(models.Track, TrackAdmin)
