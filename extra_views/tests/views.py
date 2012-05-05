from extra_views import FormSetView, ModelFormSetView, InlineFormSetView, InlineFormSet, CreateWithInlinesView, UpdateWithInlinesView, CalendarMonthArchiveView
from extra_views.generic import GenericInlineFormSet, GenericInlineFormSetView
from extra_views.sorting import SortableListMixin
from django.views import generic
    
from forms import AddressForm, ItemForm, OrderForm
from formsets import BaseArticleFormSet
from models import Item, Order, Tag, Event


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
    context_object_name = 'order'
    inlines = [ItemsInline, TagsInline]
    template_name = 'extra_views/order_and_items.html'

    def get_success_url(self):
        return '../%i' % self.object.pk


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


class EventCalendarView(CalendarMonthArchiveView):
    template_name = 'extra_views/event_calendar_month.html'    
    model = Event
    month_format='%b'
    date_field = 'date'


class SortableItemListView(SortableListMixin, generic.ListView):
    template_name = 'extra_views/sortable_item_list.html'
    sort_fields = ['name', 'sku']
    model = Item

    def get(self, request, *args, **kwargs):
        if kwargs['flag'] == 'fields_and_aliases':
            self.sort_fields_aliases = [('name', 'by_name'), ('sku', 'by_sku'), ]
        elif kwargs['flag'] == 'aliases':
            self.sort_fields_aliases = [('name', 'by_name'), ('sku', 'by_sku'), ]
            self.sort_fields = []
        return super(SortableItemListView, self).get(request, *args, **kwargs)