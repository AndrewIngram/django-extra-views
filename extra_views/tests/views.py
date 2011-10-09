from extra_views import FormSetView, ModelFormSetView, InlineFormSetView, InlineFormSet, CreateWithInlinesView, UpdateWithInlinesView
from extra_views.generic import GenericInlineFormSet, GenericInlineFormSetView
    
from forms import AddressForm, ItemForm
from formsets import BaseArticleFormSet
from models import Item, Order, Tag


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
    

class ItemsInline(InlineFormSet):
    model = Item


class TagsInline(GenericInlineFormSet):
    model = Tag


class OrderCreateView(CreateWithInlinesView):
    model = Order
    inlines = [ItemsInline, TagsInline]
    template_name = 'extra_views/order_and_items.html'

    def get_success_url(self):
        return '../%i' % self.object.pk


class OrderUpdateView(UpdateWithInlinesView):
    model = Order
    inlines = [ItemsInline, TagsInline]
    template_name = 'extra_views/order_and_items.html'

    def get_success_url(self):
        return ''


class OrderTagsView(GenericInlineFormSetView):
    model = Order
    inline_model = Tag
    template_name = "extra_views/inline_formset.html"    

