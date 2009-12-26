import os

from django import forms
from django.conf import settings
from django.core import urlresolvers
from django.forms.formsets import BaseFormSet, formset_factory
from django.utils.datastructures import SortedDict

from ..classical.models import Artist, Work, Ensemble, Instrument

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

class ChooseFilesForm(forms.Form):
    file = forms.CharField(max_length=500)

    def clean(self):
        try:
            import_base = settings.CLASSICAL_IMPORT_BASE
        except AttributeError:
            raise ImproperlyConfigured('No CLASSICAL_IMPORT_BASE in settings.py found')

        full_path = os.path.join(import_base, self.cleaned_data['file'])

        if full_path != os.path.normpath(full_path):
            raise forms.ValidationError("Path contains trickery")

        if not os.path.isfile(full_path):
            raise forms.ValidationError("%s does not exist" % full_path)

        return self.cleaned_data

ChooseFiles = formset_factory(ChooseFilesForm, formset=NonEmptyFormSet,
    extra=100)

class ChooseComposer(forms.Form):
    composer = forms.ModelChoiceField(
        Artist.objects.all(),
        widget=forms.Select(attrs={'size': 30}),
    )

class ChooseWork(forms.Form):
    work = forms.ModelChoiceField(
        Work.objects.all(),
        widget=forms.Select(attrs={'size': 45}),
    )

class PerformerForm(forms.Form):
    ensemble = forms.ModelChoiceField(
        Ensemble.objects.all(),
        required=False,
    )
    artist = forms.ModelChoiceField(
        Artist.objects.all(),
        required=False,
    )
    instrument = forms.ModelChoiceField(
        Instrument.objects.all(),
        required=False,
    )

    def clean(self):
        ensemble, artist, instrument = self.cleaned_data['ensemble'], \
            self.cleaned_data['artist'], self.cleaned_data['instrument']

        if ensemble and (artist or instrument):
            raise forms.ValidationError(
                "Cannot choose an artist/instrument with an ensemble."
            )
        elif artist and not instrument:
            raise forms.ValidationError(
                "Must choose an instrument with an artist."
            )
        elif instrument and not artist:
            raise forms.ValidationError(
                "Must choose an artist with an instrument."
            )

        return self.cleaned_data

Performers = formset_factory(PerformerForm, formset=NonEmptyFormSet, extra=99)

class ConfirmForm(forms.Form):
    pass

def generate_movement_form(filenames, suggested_names):
    fields = SortedDict()
    for num, names in enumerate(zip(filenames, suggested_names)):
        original, suggested = names
        field = forms.CharField(
            max_length=100,
            initial=suggested,
            widget=forms.TextInput(attrs={'size': 75}),
        )
        field.num = num + 1
        fields['track_%0.2d' % (num + 1)] = field

    fields['year'] = forms.IntegerField(required=False)

    return type('RecordingForm', (forms.BaseForm,), {'base_fields': fields})

##

class NewArtist(forms.ModelForm):
    class Meta:
        model = Artist
        fields = ('surname', 'forenames', 'born', 'died',)

class NewWork(forms.ModelForm):
    class Meta:
        model = Work
        fields = ('title', 'composer', 'key', 'year', 'year_question', 'nickname')

class NewInstrument(forms.ModelForm):
    class Meta:
        model = Instrument
        fields = ('noun', 'adjective',)

class NewEnsemble(forms.ModelForm):
    class Meta:
        model = Ensemble
        fields = ('name',)
