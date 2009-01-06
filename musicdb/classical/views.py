# -*- coding: utf-8 -*-

import time

from django.shortcuts import render_to_response, get_object_or_404
from django_fuse import DirectoryResponse, FileResponse, WrappedFileResponse

from musicdb.classical.models import Artist, Work, Recording, Movement, \
    Ensemble

def index(request):
    composers = Artist.objects.filter(works__isnull=False).distinct()

    return render_to_response('classical/index.html', {
        'artists': composers,
    })

def fuse_index():
    composers = Artist.objects.filter(works__isnull=False).distinct()

    return DirectoryResponse(
        composers.values_list('dir_name', flat=True),
        composers.count,
    )

def artist(request, slug):
    artist = get_object_or_404(Artist, slug=slug)

    return render_to_response('classical/artist.html', {
        'artist': artist,
    })

def ensemble(request, slug):
    ensemble = get_object_or_404(Ensemble, slug=slug)

    return render_to_response('classical/ensemble.html', {
        'ensemble': ensemble,
    })

def fuse_artist(dir_name):
    artist = get_object_or_404(Artist, dir_name=dir_name)

    return DirectoryResponse(['%s.txt' % artist.id])

def work(request, artist_slug, slug):
    work = get_object_or_404(Work, slug=slug, composer__slug=artist_slug)

    return render_to_response('classical/work.html', {
        'work': work,
    })

def stats(request):
    composers = Artist.objects.filter(works__isnull=False).distinct()

    composer_count = composers.count()
    work_count = Work.objects.count()
    recording_count = Recording.objects.count()
    movement_count = Movement.objects.count()

    anniversaries = {}
    current_year = time.localtime()[0]
    for artist in Artist.objects.all():
        for attr in ('born', 'died'):
            val = getattr(artist, attr)
            if not val:
                continue

            delta = current_year - val
            if delta % 25 == 0:
                anniversaries.setdefault(attr, []).append((artist, delta))

    return render_to_response('classical/stats.html', {
        'work_count': work_count,
        'composer_count': composer_count,
        'recording_count': recording_count,
        'movement_count': movement_count,
        'movement_average': 1.0 * movement_count / recording_count,
        'recording_average': 1.0 * recording_count / work_count,

        'anniversaries': anniversaries,
    })

def timeline(request):
    return render_to_response('classical/timeline.html')

def timeline_data(request):
    composers = Artist.objects.filter(works__isnull=False).distinct()

    return render_to_response('classical/timeline_data.xml', {
        'composers': composers.exclude(born=0, died=0),
    }, mimetype='application/xml')

def artist_timeline(request, slug):
    artist = get_object_or_404(Artist, slug=slug)

    return render_to_response('classical/artist_timeline.html', {
        'artist': artist,
    })

def artist_timeline_data(request, slug):
    artist = get_object_or_404(Artist, slug=slug)

    works = artist.works.exclude(year=0)

    return render_to_response('classical/artist_timeline_data.xml', {
        'works': works,
    }, mimetype='application/xml')
