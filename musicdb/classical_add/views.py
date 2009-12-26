import os
import urllib

from django.conf import settings
from django.http import HttpResponseRedirect, Http404
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.utils.datastructures import SortedDict

from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext

from ..utils.http import JSONResponse
from ..common.models import File, MusicFile
from ..classical.models import Artist, Work, Instrument, Ensemble, Recording, \
    ArtistPerformance, EnsemblePerformance, Movement

import forms

## Steps ###################################

class Step(object):
    form = None
    next_step = None
    parent = None

    def get_form(self, data, prefix, prev_data):
        return self.form(data, prefix=prefix)

    def get_next_step(self, request):
        return self.next_step

    def extra_context(self, request, data):
        return {}

class FilesStep(Step):
    form = forms.ChooseFiles
    next_step = 'composer'

    def extra_context(self, request, data):
        try:
            import_base = settings.CLASSICAL_IMPORT_BASE
        except AttributeError:
            raise ImproperlyConfigured('No CLASSICAL_IMPORT_BASE in settings.py found')

        suffix = request.GET.get('path', '')
        path = os.path.join(import_base, suffix)

        if not os.path.isdir(path):
            raise Http404

        if os.path.normpath(path)[:len(import_base)] != import_base:
            raise Http404

        for root, dirs, files in os.walk(path):
            break # Never recurse

        return {
            'suffix': suffix,
            'parent': os.path.dirname(suffix),
            'dirs': [
                dict(name=dir, path=os.path.join(suffix, dir)) \
                    for dir in sorted(dirs)
            ],
            'files': [
                dict(
                    name=filename,
                    size=os.path.getsize(os.path.join(path, filename)),
                    path=os.path.join(suffix, filename),
                ) \
                    for filename in sorted(files)
            ],
        }

class ComposerStep(Step):
    form = forms.ChooseComposer
    next_step = 'work'
    parent = 'files'

    def extra_context(self, request, prev_data):
        return {
            'new_artist_form': forms.NewArtist(),
        }

class WorkStep(Step):
    form = forms.ChooseWork
    next_step = 'recording'
    parent = 'composer'

    def get_form(self, data, prefix, prev_data):
        form = self.form(data, prefix=prefix)
        form.fields['work'].queryset = \
            Work.objects.filter(composer=prev_data['composer']['composer'])
        return form

    def extra_context(self, request, prev_data):
        return {
            'filenames': [os.path.basename(x['file']) for x in prev_data['files'] if x],
            'new_work_form': forms.NewWork(),
        }

def movements_from_filenames(filenames):
    if len(filenames) == 1:
        return ["-"]

    import os
    import re

    filenames = [os.path.basename(x) for x in filenames]
    filenames = [re.sub('\.[^\.]+$', '', x) for x in filenames]

    while True:
        prev = list(filenames)

        common_prefix = os.path.commonprefix(filenames)
        filenames = [x[len(common_prefix):] for x in filenames]

        reverse_filenames = [x[::-1] for x in filenames]
        common_suffix = os.path.commonprefix(reverse_filenames)
        if len(common_suffix) >= 3:
            filenames = [x[:-len(common_suffix)] for x in filenames]

        filenames = [re.sub('^[\d_\.\-\siIvVxX\[\]]+', '', x) for x in filenames]

        if filenames == prev:
            break

    filenames = [re.sub('[_\s]+', ' ', x) for x in filenames]

    filenames = [x or '(unknown)' for x in filenames]
    filenames = [x[0].capitalize() + x[1:] for x in filenames]
    filenames = [re.sub('( = |\. )', ': ', x) for x in filenames]

    return filenames

class RecordingStep(Step):
    next_step = 'performers'
    parent = 'work'

    def get_form(self, data, prefix, prev_data):
        filenames = [x['file'] for x in prev_data['files'] if x]
        suggested_names = movements_from_filenames(filenames)

        form = forms.generate_movement_form(filenames, suggested_names)

        return form(data, prefix=prefix)

class PerformersStep(Step):
    next_step = 'confirm'
    parent = 'recording'
    form = forms.Performers

    def extra_context(self, request, data):
        return {
            'artists': Artist.objects.all(),
            'instruments': Instrument.objects.all(),
            'ensemble': Ensemble.objects.all(),

            'artist_form': forms.NewArtist(),
            'ensemble_form': forms.NewEnsemble(),
            'instrument_form': forms.NewInstrument(),
        }

class ConfirmStep(Step):
    next_step = None
    parent = 'performers'
    form = forms.ConfirmForm

    def extra_context(self, request, data):
        return {
            'tracks': [
                y for x, y in data['recording'].items() if x.startswith('track_')
            ],
        }

## Add view ##############################

class AddRecording(object):
    INITIAL_STEP = 'files'

    STEPS = {
        'files':        FilesStep(),
        'composer':     ComposerStep(),
        'work':         WorkStep(),
        'recording':    RecordingStep(),
        'performers':   PerformersStep(),
        'confirm':      ConfirmStep(),
    }

    def get_dependencies(self, step):
        depends = []
        parent = self.STEPS[step].parent
        if parent is not None:
            depends.extend(self.get_dependencies(parent))
        depends.append(step)
        return depends

    def __call__(self, request, *args, **kwargs):
        prev_data = {}
        prev_fields = []

        def get_form(step, data=None):
            return self.STEPS[step].get_form(data, step, prev_data)

        cur_step = request.POST.get('step', self.INITIAL_STEP)

        if request.POST:
            for step in self.get_dependencies(cur_step):
                form = get_form(step, request.POST)

                if not form.is_valid():
                    break

                prev_data[step] = form.cleaned_data

                if hasattr(form, 'forms'):
                    for inner_form in form.forms:
                        prev_fields.extend([x.as_hidden() for x in inner_form])
                    prev_fields.extend([x.as_hidden() for x in form.management_form])
                else:
                    prev_fields.extend([x.as_hidden() for x in form])
        else:
            form = get_form(cur_step)

        if form.is_valid():
            cur_step = self.STEPS[step].get_next_step(request)

            if cur_step is None:
                return self.done(prev_data)
            form = get_form(cur_step)

        context = {
            'step': cur_step,
            'form': form,
            'previous_fields': ''.join(prev_fields),
            'data': prev_data,
        }

        context.update(self.extra_context(request, prev_data))
        context.update(self.STEPS[cur_step].extra_context(request, prev_data))

        return render_to_response(
            self.get_template(cur_step),
            context,
            context_instance=RequestContext(request)
        )

    def done(self, data):
        recording = Recording.objects.create(
            work=data['work']['work'],
            year=data['recording']['year'],
        )

        for idx, performer in enumerate(filter(bool, data['performers'])):
            if 'artist' in performer:
                ArtistPerformance.objects.create(
                    num=idx + 1,
                    recording=recording,
                    artist=performer['artist'],
                    instrument=performer['instrument'],
                )
            else:
                EnsemblePerformance.objects.create(
                    num=idx + 1,
                    recording=recording,
                    ensemble=performer['ensemble'],
                )

        recording.save() # Refresh slug to include performers

        titles = [y for x, y in data['recording'].items() if x.startswith('track_')]
        files = zip(titles, [x['file'] for x in data['files'] if x])

        music_files = []

        for idx, file_info in enumerate(files):
            title, path = file_info

            import_base = settings.CLASSICAL_IMPORT_BASE
            full_path = os.path.join(import_base, path)

            """
            file = File.objects.create(
                location='dummy.%d-%d.mp3' % (recording.id, idx + 1),
                size=os.path.getsize(full_path),
            )
            """

            _, extension = os.path.splitext(full_path)

            file = File.create_from_path(
                full_path,
                'classical/%d/%.2d%s' % (recording.id, idx + 1, extension)
            )

            music_file = MusicFile.objects.create(
                file=file,
                rev_model='movement',
                tags_dirty=True,
            )

            Movement.objects.create(
                recording=recording,
                title=title,
                music_file=music_file,
                num=idx + 1,
            )

            music_files.append(music_file)

        for music_file in music_files:
            music_file.tag()

        common_dir = os.path.dirname(os.path.commonprefix(
            [x['file'] for x in data['files'] if x]
        ))

        return HttpResponseRedirect("%s?%s" % (
            reverse('classical-add-recording-done', args=(recording.id,)),
            urllib.urlencode({'next': common_dir}),
        ))

    def get_template(self, step):
        return 'classical_add/%s.html' % step

    def extra_context(self, request, data):
        try:
            previous_recording = Recording.objects.order_by('-pk')[0]
        except KeyError:
            previous_recording = None

        return {
            'previous_recording': previous_recording,
        }

def done(request, recording_id):
    context = {
        'recording': get_object_or_404(Recording, id=recording_id),
        'next': request.GET.get('next'),
    }

    return render_to_response(
        'classical_add/done.html',
        context,
        context_instance=RequestContext(request)
    )

def _helper(form):
    if not form.is_valid():
        print form.errors
        assert False
    obj = form.save()
    return JSONResponse({
        'object_id': obj.pk,
        'object': unicode(obj),
    })

def add_artist(request):
    form = forms.NewArtist(request.POST)
    return _helper(form)

def add_work(request):
    form = forms.NewWork(request.POST)
    return _helper(form)

def add_instrument(request):
    form = forms.NewInstrument(request.POST)
    return _helper(form)

def add_ensemble(request):
    form = forms.NewEnsemble(request.POST)
    return _helper(form)
