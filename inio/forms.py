from django import forms
from django.forms import ModelForm
from .models import UploadFileModel

class SearchForm(forms.Form):
    search_keyword = forms.CharField(label='Search', max_length=300)

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadFileModel
        fields = ('title', 'file')