from django import forms
from django.forms import ModelForm, Textarea, widgets
from .models import Reservations
from django.db import models
from time import gmtime, strftime
from datetime import timedelta, datetime


class DateInput(forms.DateInput):
    input_type = 'date'
def setTime():
    date_N_days_ago = datetime.now() + timedelta(days=1)


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservations
        fields = ['name', 'surname', 'check_in', 'check_out', 'people']
        widgets = {
            'check_in': DateInput(),
            'check_out': DateInput(),
            'people': forms.NumberInput(attrs={'min': 1, 'max': 4})
        }



    def __init__(self, *args, **kwargs):
        super(ReservationForm, self).__init__(*args, **kwargs)
        self.fields['check_in'].widget.attrs['value'] = strftime("%Y-%m-%d", gmtime())
        self.fields['check_in'].widget.attrs['min'] = strftime("%Y-%m-%d", gmtime())
        self.fields['check_out'].widget.attrs['min'] = format(datetime.now()+timedelta(days=1),"%Y-%m-%d")
        self.fields['check_out'].widget.attrs['value'] = format(datetime.now()+timedelta(days=1),"%Y-%m-%d")