from django import forms
from django.forms.formsets import BaseFormSet
from django.forms.models import BaseModelFormSet

COUNTRY_CHOICES = (
    ("gb", "Great Britain"),
    ("us", "United States"),
    ("ca", "Canada"),
    ("au", "Australia"),
    ("nz", "New Zealand"),
)


class AddressFormSet(BaseFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.fields["county"] = forms.ChoiceField(choices=COUNTRY_CHOICES, initial="gb")


class BaseArticleFormSet(BaseModelFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.fields["notes"] = forms.CharField(initial="Write notes here")
