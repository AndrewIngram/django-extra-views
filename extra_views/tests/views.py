from extra_views import FormSetView, ModelFormSetView, InlineFormSetView, MultiFormView
from forms import AddressForm, ItemForm
from formsets import BaseArticleFormSet
from models import Item, Order


class AddressFormSetView(FormSetView):
    form_class = AddressForm
    template_name = 'extra_views/address_formset.html'


class ItemModelFormSetView(ModelFormSetView):
    model = Item
    template_name = 'extra_views/item_formset.html'


class FormAndFormSetOverrideView(ModelFormSetView):
    model = Item
    form_class = ItemForm
    formset_class = BaseArticleFormSet
    template_name = 'extra_views/item_formset.html'


class OrderItemFormSetView(InlineFormSetView):
    model = Order
    inline_model = Item
    template_name = "extra_views/inline_formset.html"


class PagedModelFormSetView(ModelFormSetView):
    paginate_by = 2
    model = Item
    template_name = 'extra_views/paged_formset.html'


class SimpleMultiView(MultiFormView):
    forms = {
        'order': MultiFormView.modelform(Order),
        'address': MultiFormView.form(AddressForm),
    }
    template_name = 'extra_views/orderaddress_multiview.html'
    
    def get_order_instance(self):
        return None
  

class OrderAndAddressView(MultiFormView):
    forms = {
        'order': MultiFormView.modelform(Order),
        'address': MultiFormView.form(AddressForm),
    }
    groups = {
        'order_and_address': ('order', 'address'),
        'order': ('order', )
    }
    template_name = 'extra_views/orderaddress_multiview.html'
    
    def get_order_instance(self):
        return None
    
    def valid_order_and_address(self, forms):
        forms['order'].save()
    
    def valid_order(self, forms):
        forms['order'].save()


class InvalidMultiFormView(MultiFormView):
    forms = {
        'order': MultiFormView.modelform(Order),
        'address': MultiFormView.form(AddressForm),
    }
    groups = {
        'order_and_address': ('order', 'address'),
        'order': ('order', )
    }
    template_name = 'extra_views/orderaddress_multiview.html'    
    
    
class OrderAndItemsView(MultiFormView):
    forms = {
        'order': MultiFormView.modelform(Order),
        'items': MultiFormView.modelformset(Item, form=ItemForm),
    }
    groups = {
        'order_and_items': ('order', 'items'),
        'order': ('order' ,)
    }
    template_name = 'extra_views/orderitems_multiview.html'
    
    def get_items_queryset(self):
        return Item.objects.all().none()
    
    def get_order_instance(self):
        return None
    
    def valid_order_and_items(self, forms):
        pass
    
    def valid_order(self, forms):
        pass

    
#class MultiViewHandler(MultiFormView):
#    forms = {
#        'order': OrderForm,
#        'address': AddressForm,
#    }
#    template_name = 'extra_views/orderaddress_multiview.html'
#    
#    def handle_valid_order(self, form, valid_forms):
#        self.request.session['valid_order'] = form.cleaned_data['name']
#    
#    def handle_invalid_address(self, form, invalid_forms):
#        self.request.session['invalid_address'] = 'Error'
#        
#    def handle_valid(self, forms, valid_forms):
#        self.request.session['forms_valid'] = 'All'
#    
#    def handle_invalid(self, forms, invalid_forms):
#        self.request.session['forms_invalid'] = 'Any'
#        
#class MultiViewInitialData(MultiFormView):
#    forms = {
#        'order': OrderForm,
#        'address': AddressForm,
#    }
#    template_name = 'extra_views/orderaddress_multiview.html'    
#    initial = {
#        'order': {
#            'name': 'Sally Jones',
#        },
#        'address': {
#            'name': 'Sally Jones',
#            'line1': '123 Generic Road',
#            'line2': 'Little Village',
#            'city': 'Big City',
#            'postcode': 'ABC 123',
#        }
#    }
#    
#class MultiViewInitialHandlers(MultiFormView):
#    forms = {
#        'order': OrderForm,
#        'address': AddressForm,
#    }
#    template_name = 'extra_views/orderaddress_multiview.html'    
#    
#    def get_initial_order(self):
#        return {
#            'name': 'Bob Jones',                
#        }
#    
#    def get_initial_address(self):
#        return {
#            'name': 'Bob Jones',
#            'line1': '123 Generic Road',
#            'line2': 'Big Village',
#            'city': 'Little City',
#            'postcode': 'XYZ 789',
#        }
#
#class MultiViewWithFormSets(MultiFormView):
#    template_name = 'extra_views/formsets_multiview.html'       
#    forms = {
#        'order': OrderForm, 
#    }
#    formsets = {
#        'items': modelformset_factory(model=Item),
#    }
#    def get_items_kwargs(self):
#        return dict(queryset=Item.objects.all())
    