from extra_views import FormsetView, ModelFormsetView
from forms import ItemForm, AddressForm
from models import Order, Item


class AddressFormsetView(FormsetView):
    form_class = AddressForm
    template_name = 'extra_views/address_formset.html'
    
class ItemModelFormsetView(ModelFormsetView):
    model = Item
    template_name = 'extra_views/item_formset.html'    