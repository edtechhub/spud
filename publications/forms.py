from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_min(value1, value2):
    if value1 >= value2:
        raise ValidationError(
            _('%(value)s Min_hdi is larger than Max_hdi'),
            params={'value1': value1, 'value2':value2},
        )

class SearchForm(forms.Form):
	tak = forms.CharField(required=False, max_length=100)
    year = forms.IntegerField(required=False)
    author = forms.CharField(required=False, max_length=100)
    search_engine = forms.BooleanField()
    highlight_param = forms.BooleanField()
    min_hdi = forms.FloatField(required=False, max_value=1, min_value=0, widget=NumberInput(attrs={'id': 'min_hdi', 'step': "0.01"}))
	max_hdi = forms.FloatField(required=False, max_value=1, min_value=0, widget=NumberInput(attrs={'id': 'max_hdi', 'step': "0.01"}))


	form_gc = forms.MultipleChoiceField(required=False)
	#MultipleChoiceField
	form_gr = request.GET.getlist('GR filter')
	form_f = request.GET.getlist('F filter')
	form_gd = request.GET.getlist('GD filter')
	form_o = request.GET.getlist('O filter')
	form_p1 = request.GET.getlist('P1 filter')
	form_p2 = request.GET.getlist('P2 filter')
	form_r = request.GET.getlist('R filter')
	form_te = request.GET.getlist('TE filter')
	form_tt = request.GET.getlist('TT filter')