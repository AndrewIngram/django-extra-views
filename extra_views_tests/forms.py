from django import forms

from .models import Item, Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["name"]

    def save(self, commit=True):
        instance = super().save(commit=commit)

        if commit:
            instance.action_on_save = True
            instance.save()

        return instance


class ItemForm(forms.ModelForm):
    flag = forms.BooleanField(initial=True)

    class Meta:
        model = Item
        fields = ["name", "sku", "price", "order", "status"]


class AddressForm(forms.Form):
    name = forms.CharField(max_length=255, required=True)
    line1 = forms.CharField(max_length=255, required=False)
    line2 = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=255, required=False)
    postcode = forms.CharField(max_length=10, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
