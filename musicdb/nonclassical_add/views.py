import os

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse

from ..common.forms import Step, AbstractAddView, AbstractFilesStep, \
    AbstractConfirmStep, generate_track_form

from ..common.models import File, MusicFile
from ..nonclassical.models import Album, CD, Track

import forms

## Add view ##############################

class AddRecording(AbstractAddView):
    INITIAL_STEP = 'files'

    ## Steps ###########################################

    class FilesStep(AbstractFilesStep):
        import_base = settings.NON_CLASSICAL_IMPORT_BASE
        next_step = 'album'

    class AlbumStep(Step):
        form = forms.AlbumInfoForm
        next_step = 'tracks'
        parent = 'files'

    class TrackStep(Step):
        next_step = 'confirm'
        parent = 'album'

        def get_form(self, data, prefix, prev_data):
            filenames = [x['file'] for x in prev_data['files'] if x]
            suggested_names = track_names_from_filenames(filenames)

            form = generate_track_form(filenames, suggested_names)

            return form(data, prefix=prefix)

    class ConfirmStep(AbstractConfirmStep):
        parent = 'tracks'

    STEPS = {
        'files':    FilesStep(),
        'album':    AlbumStep(),
        'tracks':   TrackStep(),
        'confirm':  ConfirmStep(),
    }

    def get_template(self, step):
        return 'nonclassical_add/%s.html' % step

    def done(self, data):
        titles = [y for x, y in data['tracks'].items() if x.startswith('track_')]
        files = zip(titles, [x['file'] for x in data['files'] if x])

        cd = []
        for title, path in files:
            cd.append({
                'title':    title,
                'path':     os.path.join(self.FilesStep.import_base, path),
            })

        album = Album.add_album({
            'artist':   data['album']['artist'],
            'title':    data['album']['title'],
            'year':     data['album']['year'],
            'cds':      [cd],
        })

        return HttpResponseRedirect(
           reverse('non-classical-add-recording-done', args=(album.id,))
        )

def done(request, album_id):
    context = {
        'album': get_object_or_404(Album, id=album_id),
    }

    return render_to_response(
        'nonclassical_add/done.html',
        context,
        context_instance=RequestContext(request)
    )
