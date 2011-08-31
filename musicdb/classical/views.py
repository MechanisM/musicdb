# -*- coding: utf-8 -*-

import time

from django.shortcuts import render_to_response, get_object_or_404
from django_fuse import DirectoryResponse, FileResponse

from musicdb.utils.http import XSPFResponse
from musicdb.classical.models import Artist, Work, Recording, Movement, \
    Ensemble, Category

def index(request):
    return render_to_response('classical/index.html')

def categories(request):
    return render_to_response('classical/categories.html', {
        'categories': Category.get_root_nodes(),
    })

def category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)

    return render_to_response('classical/category.html', {
        'category': category,
    })

def composers(request):
    return render_to_response('classical/composers.html', {
        'composers': Artist.objects.composers(),
    })

def ensembles(request):
    return render_to_response('classical/ensembles.html', {
        'ensembles': Ensemble.objects.all(),
    })

def artists(request):
    return render_to_response('classical/artists.html', {
        'artists': Artist.objects.artists(),
    })

def artist(request, slug):
    return render_to_response('classical/artist.html', {
        'artist': get_object_or_404(Artist, slug=slug),
    })

def ensemble(request, slug):
    return render_to_response('classical/ensemble.html', {
        'ensemble': get_object_or_404(Ensemble, slug=slug),
    })

def work(request, artist_slug, slug):
    return render_to_response('classical/work.html', {
        'work': get_object_or_404(Work, slug=slug, composer__slug=artist_slug),
    })

def play_recording(request, recording_id):
    recording = get_object_or_404(Recording, id=recording_id)
    return XSPFResponse(recording.get_tracks())

##

def fuse_index():
    return DirectoryResponse(
        Artist.objects.composers().values_list('dir_name', flat=True),
    )

def fuse_artist(dir_name):
    artist = get_object_or_404(Artist, dir_name=dir_name)

    return DirectoryResponse()

##

def stats(request):
    composer_count = Artist.objects.composers().count()
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
            if delta % 50 == 0:
                anniversaries.setdefault(attr, []).append((artist, delta))

    artists_by_num_works = Artist.objects.by_num_works()[:10]
    works_by_num_recordings = Work.objects.by_num_recordings()[:10]

    return render_to_response('classical/stats.html', {
        'work_count': work_count,
        'composer_count': composer_count,
        'recording_count': recording_count,
        'movement_count': movement_count,
        'movement_average': recording_count and 1.0 * movement_count / recording_count or 0,
        'recording_average': work_count and 1.0 * recording_count / work_count or 0,

        'anniversaries': anniversaries,
        'artists_by_num_works': artists_by_num_works,
        'works_by_num_recordings': works_by_num_recordings,
    })

def timeline(request):
    return render_to_response('classical/timeline.html')

def timeline_data(request):
    composers = Artist.objects.composers()

    return render_to_response('classical/timeline_data.xml', {
        'composers': composers.exclude(born=0, died=0),
    }, mimetype='application/xml')

def artist_timeline(request, slug):
    return render_to_response('classical/artist_timeline.html', {
        'artist': get_object_or_404(Artist, slug=slug),
    })

def artist_timeline_data(request, slug):
    artist = get_object_or_404(Artist, slug=slug)

    return render_to_response('classical/artist_timeline_data.xml', {
        'works': artist.works.exclude(year=0),
    }, mimetype='application/xml')
