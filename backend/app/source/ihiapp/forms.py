from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Device

class FetchDataForm(forms.Form):
    start_datetime = forms.DateTimeField(
        label='開始日時',
        input_formats=['%Y-%m-%d %H:%M'],
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%d %H:%M')
    )
    end_datetime = forms.DateTimeField(
        label='終了日時',
        input_formats=['%Y-%m-%d %H:%M'],
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%d %H:%M')
    )

    def __init__(self, *args, **kwargs):
        super(FetchDataForm, self).__init__(*args, **kwargs)
