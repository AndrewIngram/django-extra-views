from django import forms
from .models import Order, Item


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order

    def save(self, commit=True):
        instance = super(OrderForm, self).save(commit=commit)

        if commit:
            instance.action_on_save = True
            instance.save()

        return instance


class ItemForm(forms.ModelForm):
    flag = forms.BooleanField(initial=True)

    class Meta:
        model = Item


class AddressForm(forms.Form):
    name = forms.CharField(max_length=255, required=True)
    line1 = forms.CharField(max_length=255, required=False)
    line2 = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=255, required=False)
    postcode = forms.CharField(max_length=10, required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(AddressForm, self).__init__(*args, **kwargs)
