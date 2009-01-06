# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect

from django_fuse import DirectoryResponse, FileResponse

from musicdb.nonclassical.models import Artist, Album

def index(request, letter='a'):
    if letter is None:
        return HttpResponseRedirect('a')

    letters = Artist.objects.values_list('name_first', flat=True). \
        order_by('name_first').distinct()

    artists = Artist.objects.filter(name_first=letter)

    return render_to_response('nonclassical/index.html', {
        'letters': letters,
        'artists': artists,
    })

def fuse_index():
    artists = Artist.objects.all()

    return DirectoryResponse(
        artists.values_list('dir_name', flat=True),
        artists.count,
    )

def artist(request, slug):
    artist = get_object_or_404(Artist, slug=slug)

    return render_to_response('nonclassical/artist.html', {
        'artist': artist,
    })

def fuse_artist(dir_name):
    artist = get_object_or_404(Artist, dir_name=dir_name)

    albums = artist.albums()

    return DirectoryResponse(
        albums.values_list('dir_name', flat=True),
        albums.count,
    )

def album(request, artist_slug, slug):
    album = get_object_or_404(Album,
        slug=slug,
        cds__num=1,
        cds__tracks__num=1,
        cds__tracks__performers__artist__slug=artist_slug,
    )

    return render_to_response('nonclassical/album.html', {
        'album': album,
    })

def fuse_album(artist_dir_name, dir_name):
    album = get_object_or_404(Album,
        dir_name=dir_name,
        cds__num=1,
        cds__tracks__num=1,
        cds__tracks__performers__artist__slug=artist_dir_name,
    )

    return DirectoryResponse([])
