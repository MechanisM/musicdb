from django.db.models import Sum
from django.shortcuts import get_object_or_404, render

from musicdb.utils.http import XSPFResponse

from .models import MusicFile

def play_music_file(request, music_file_id):
    music_file = get_object_or_404(MusicFile, id=music_file_id)
    return XSPFResponse([music_file])

def stats(request):
    return render(request, 'common/stats.html', {
        'music_file_count': MusicFile.objects.count(),
        'total_duration': MusicFile.objects.aggregate(Sum('length'))['length__sum'] or 0,
    })
