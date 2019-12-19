from django import forms
from django.forms.widgets import NumberInput

from app.models import Constant, DistributionDropdown, DistributionSlider

# TODO: https://docs.djangoproject.com/en/2.2/topics/forms/formsets/


class RangeInput(NumberInput):
    input_type = 'range'


class ConstantForm(forms.ModelForm):
    class Meta:
        model = Constant
        fields = []


# class DistributionDropdownForm(forms.ModelForm):
#     class Meta:
#         model = DistributionDropdown
#         fields = ['low_value', 'mid_value', 'high_value']


class DistributionSliderForm(forms.ModelForm):

    class Meta:
        model = DistributionSlider
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        low_value = self.instance.low_value
        mid_value = self.instance.mid_value
        high_value = self.instance.high_value
        step = self.instance.step

        self.fields['range_field'] = forms.IntegerField(
            widget=RangeInput(attrs={'min': low_value, 'max': high_value, 'step': step, 'value': mid_value})
        )
        self.fields['range_field'].label = self.instance.label
