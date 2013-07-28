from extra_views import FormSetView, ModelFormSetView, InlineFormSetView, InlineFormSet, CreateWithInlinesView, UpdateWithInlinesView, CalendarMonthView, NamedFormsetsMixin, SortableListMixin, SearchableListMixin
from extra_views.generic import GenericInlineFormSet, GenericInlineFormSetView
from django.views import generic
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


class AddressFormSetViewNamed(NamedFormsetsMixin, AddressFormSetView):
    inlines_names = ['AddressFormset']


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


class OrderCrateNamedView(NamedFormsetsMixin, OrderCreateView):
    inlines_names = ['Items', 'Tags']


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


class EventCalendarView(CalendarMonthView):
    template_name = 'extra_views/event_calendar_month.html'
    model = Event
    month_format = '%b'
    date_field = 'date'


class SearchableItemListView(SearchableListMixin, generic.ListView):
    template_name = 'extra_views/item_list.html'
    search_fields = ['name', 'sku']
    search_date_fields = ['date_placed']
    model = Item
    define_query = False
    exact_query = False
    wrong_lookup = False

    def get_search_query(self):
        if self.define_query:
            return 'test B'
        else:
            return super(SearchableItemListView, self).get_search_query()

    def get(self, request, *args, **kwargs):
        if self.exact_query:
            self.search_fields = [('name', 'iexact'), 'sku']
        elif self.wrong_lookup:
            self.search_fields = [('name', 'gte'), 'sku']
        return super(SearchableItemListView, self).get(request, *args, **kwargs)


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
