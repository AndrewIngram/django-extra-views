from extra_views import FormSetView, ModelFormSetView, InlineFormSetView, GenericInlineFormSetView
from extra_views import CreateWithInlinesView, UpdateWithInlinesView
from extra_views import InlineFormSet, GenericInlineFormSet
from .forms import AddressForm, ItemForm, OrderForm
from .formsets import BaseArticleFormSet
from .models import Item, Order, Tag, Event


class AddressFormSetView(FormSetView):
    form_class = AddressForm
    template_name = 'extra_views/address_formset.html'

    def get_extra_form_kwargs(self):
        return {
            'user': 'foo',
        }


class AddressFormSetViewNamed(AddressFormSetView):
    formset_context_name = 'AddressFormset'


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
    context_object_name = 'order'
    inlines = [ItemsInline, TagsInline]
    template_name = 'extra_views/order_and_items.html'

    def get_success_url(self):
        return '../%i' % self.object.pk


class OrderCrateNamedView(OrderCreateView):
    inline_context_names = ['Items', 'Tags']


class OrderUpdateView(UpdateWithInlinesView):
    model = Order
    form_class = OrderForm
    inlines = [ItemsInline, TagsInline]
    template_name = 'extra_views/order_and_items.html'

    def get_success_url(self):
        return ''


class OrderTagsView(GenericInlineFormSetView):
    model = Order
    inline_model = Tag
    template_name = "extra_views/inline_formset.html"
