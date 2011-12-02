# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404

from django_fuse import DirectoryResponse, SymlinkResponse

from musicdb.utils.http import XSPFResponse
from musicdb.nonclassical.models import Artist, Album, CD, Track

def index(request, letter='a'):
    if letter is None:
        return HttpResponseRedirect('a')

    letters = Artist.objects.values_list('name_first', flat=True). \
        order_by('name_first').distinct()

    artists = Artist.objects.filter(name_first=letter)

    return render(request, 'nonclassical/index.html', {
        'letters': letters,
        'artists': artists,
    })

def artist(request, slug):
    artist = get_object_or_404(Artist, slug=slug)

    return render(request, 'nonclassical/artist.html', {
        'artist': artist,
    })

def album(request, artist_slug, slug):
    try:
        album = Album.objects.get_from_slugs(artist_slug, slug)
    except Album.DoesNotExist:
        raise Http404

    return render(request, 'nonclassical/album.html', {
        'album': album,
    })

def play_cd(request, cd_id):
    cd = get_object_or_404(CD, id=cd_id)

    return XSPFResponse(cd.get_tracks())

def play_album(request, album_id):
    album = get_object_or_404(Album, id=album_id)

    return XSPFResponse(album.get_tracks())

def collage(request):
    albums = Album.objects.exclude(cover='')

    return render(request, 'nonclassical/collage.html', {
        'albums': albums,
    })

##

def fuse_index():
    artists = Artist.objects.all()

    return DirectoryResponse(artists.values_list('dir_name', flat=True))

def fuse_artist(dir_name):
    artist = get_object_or_404(Artist, dir_name=dir_name)

    albums = artist.albums()

    return DirectoryResponse(albums.values_list('dir_name', flat=True))

def fuse_album(artist_dir_name, dir_name):
    try:
        album = Album.objects.get_from_dir_name(artist_dir_name, dir_name)
    except Album.DoesNotExist:
        raise Http404

    tracks = album.get_nonclassical_tracks()

    return DirectoryResponse(tracks.values_list('dir_name', flat=True))

def fuse_track(artist_dir_name, album_dir_name, dir_name):
    try:
        album = Album.objects.get_from_dir_name(artist_dir_name, album_dir_name)
        track = Track.objects.get_from_dir_name(dir_name, album)
    except (Album.DoesNotExist, Track.DoesNotExist):
        raise Http404()

    return SymlinkResponse('/mnt/raid/share/mp3/%s' % track.track.file.location)

