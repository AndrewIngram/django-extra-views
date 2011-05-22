from extra_views import FormsetView, ModelFormsetView, MultiView
from forms import AddressForm, OrderForm
from models import Item


class AddressFormsetView(FormsetView):
    form_class = AddressForm
    template_name = 'extra_views/address_formset.html'


class ItemModelFormsetView(ModelFormsetView):
    model = Item
    template_name = 'extra_views/item_formset.html'

    
class OrderAndAddressView(MultiView):
    forms = {
        'order': OrderForm,
        'address': AddressForm,
    }
    template_name = 'extra_views/orderaddress_multiview.html'