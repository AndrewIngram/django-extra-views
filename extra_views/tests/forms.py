from django import forms
from models import Order, Item


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        

class AddressForm(forms.Form):
    name = forms.CharField(max_length=255)
    line1 = forms.CharField(max_length=255)
    line2 = forms.CharField(max_length=255)
    city = forms.CharField(max_length=255)
    postcode = forms.CharField(max_length=10)
