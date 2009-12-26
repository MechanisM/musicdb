from django import forms

from ..nonclassical.models import Artist

class AlbumInfoForm(forms.Form):
    artist = forms.ModelChoiceField(
        Artist.objects.all(),
    )
    title = forms.CharField()
    year = forms.IntegerField(required=False)
