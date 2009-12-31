import os.path
import operator

from django import forms
from django.shortcuts import render_to_response, Http404
from django.forms.formsets import BaseFormSet, formset_factory
from django.template.context import RequestContext

class NonEmptyFormSet(BaseFormSet):
    def clean(self):
        if not self.is_valid():
            return
        data = [x for x in self.cleaned_data if x]

        if len(data) == 0:
            raise forms.ValidationError("Must complete at least one FormSet")

        unique = []
        for x in data:
            if x in unique:
                raise forms.ValidationError("Duplicate element")
            unique.append(x)

def generate_track_form(filenames, suggested_names, **fields):
    fields = {}
    for num, names in enumerate(zip(filenames, suggested_names)):
        original, suggested = names
        field = forms.CharField(
            max_length=100,
            initial=suggested,
            help_text=os.path.basename(original),
            widget=forms.TextInput(attrs={'size': 35})
        )
        fields['track_%0.2d' % (num + 1)] = field
    return type('TrackForm', (forms.BaseForm,), {'base_fields': fields})

## Steps

class Step(object):
    form = None
    next_step = None
    parent = None

    def get_form(self, data, prefix, prev_data):
        return self.form(data, prefix=prefix)

    def get_next_step(self, request):
        return self.next_step

    def extra_context(self, request):
        return {}

class AbstractAddView(object):
    INITIAL_STEP = None
    STEPS = {}

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
        try:
            sorted_fields = list(form)
            sorted_fields.sort(key=operator.attrgetter('name'))
            context.update({'sorted_fields': sorted_fields})
        except TypeError:
            # FormSets are not iterable
            pass

        context.update(self.STEPS[cur_step].extra_context(request))

        return render_to_response(
            self.get_template(cur_step),
            context,
            context_instance=RequestContext(request)
        )

class AbstractFilesStep(Step):
    next_step = None
    import_base = None

    def get_form(self, data, prefix, prev_data):
        import_base = self.import_base

        class ChooseFilesForm(forms.Form):
            file = forms.CharField(max_length=500)

            def clean(self):
                full_path = os.path.join(import_base, self.cleaned_data['file'])

                if full_path != os.path.normpath(full_path):
                    raise forms.ValidationError("Path contains trickery")

                if not os.path.isfile(full_path):
                    raise forms.ValidationError("%s does not exist" % full_path)

                self.cleaned_data['basename'] = os.path.basename(full_path)
                self.cleaned_data['dirname'] = \
                    os.path.dirname(self.cleaned_data['file'])

                return self.cleaned_data

        return formset_factory(
            ChooseFilesForm,
            formset=NonEmptyFormSet,
            extra=100,
        )(data, prefix=prefix)

    def extra_context(self, request):
        suffix = request.GET.get('path', '')
        path = os.path.join(self.import_base, suffix)

        if not os.path.isdir(path):
            raise Http404

        if os.path.normpath(path)[:len(self.import_base)] != self.import_base:
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

class AbstractConfirmStep(Step):
    class ConfirmForm(forms.Form):
        pass

    next_step = None
    form = ConfirmForm

    parent = None
