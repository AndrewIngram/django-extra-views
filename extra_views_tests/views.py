from django.views import generic

from extra_views import (
    CalendarMonthView,
    CreateWithInlinesView,
    FormSetSuccessMessageMixin,
    FormSetView,
    InlineFormSetFactory,
    InlineFormSetView,
    ModelFormSetView,
    NamedFormsetsMixin,
    SearchableListMixin,
    SortableListMixin,
    SuccessMessageMixin,
    UpdateWithInlinesView,
)
from extra_views.generic import GenericInlineFormSetFactory, GenericInlineFormSetView

from .forms import AddressForm, ItemForm, OrderForm
from .formsets import BaseArticleFormSet
from .models import Event, Item, Order, Tag


class AddressFormSetView(FormSetSuccessMessageMixin, FormSetView):
    form_class = AddressForm
    template_name = "extra_views/address_formset.html"
    success_message = "Formset objects were created successfully!"


class AddressFormSetViewNamed(NamedFormsetsMixin, AddressFormSetView):
    inlines_names = ["AddressFormset"]


class AddressFormSetViewKwargs(FormSetView):
    # Used for testing class level kwargs
    form_class = AddressForm
    template_name = "extra_views/address_formset.html"
    formset_kwargs = {"auto_id": "id_test_%s", "form_kwargs": {"empty_permitted": True}}
    factory_kwargs = {"max_num": 27}
    prefix = "test_prefix"
    initial = [{"name": "address1"}]


class ItemModelFormSetView(ModelFormSetView):
    model = Item
    fields = ["name", "sku", "price", "order", "status"]
    template_name = "extra_views/item_formset.html"


class ItemModelFormSetExcludeView(ModelFormSetView):
    model = Item
    exclude = ["sku", "price"]
    template_name = "extra_views/item_formset.html"


class FormAndFormSetOverrideView(ModelFormSetView):
    model = Item
    form_class = ItemForm
    formset_class = BaseArticleFormSet
    template_name = "extra_views/item_formset.html"


class OrderItemFormSetView(InlineFormSetView):
    model = Order
    fields = ["name", "sku", "price", "order", "status"]
    inline_model = Item
    template_name = "extra_views/inline_formset.html"


class PagedModelFormSetView(ModelFormSetView):
    paginate_by = 2
    model = Item
    template_name = "extra_views/paged_formset.html"


class ItemsInline(InlineFormSetFactory):
    model = Item
    fields = ["name", "sku", "price", "order", "status"]


class TagsInline(GenericInlineFormSetFactory):
    model = Tag
    fields = ["name"]


class OrderCreateView(SuccessMessageMixin, CreateWithInlinesView):
    model = Order
    fields = ["name"]
    context_object_name = "order"
    inlines = [ItemsInline, TagsInline]
    template_name = "extra_views/order_and_items.html"
    success_message = "Order %(name)s was created successfully!"

    def form_valid(self, form):
        response = super().form_valid(form)
        # Update the response url to indicate that form_valid was called
        response["Location"] += "?form_valid_called=1"
        return response


class OrderCreateNamedView(NamedFormsetsMixin, OrderCreateView):
    inlines_names = ["Items", "Tags"]


class OrderUpdateView(UpdateWithInlinesView):
    model = Order
    form_class = OrderForm
    inlines = [ItemsInline, TagsInline]
    template_name = "extra_views/order_and_items.html"


class OrderTagsView(GenericInlineFormSetView):
    model = Order
    inline_model = Tag
    template_name = "extra_views/inline_formset.html"
    initial = [{"name": "test_tag_name"}]


class EventCalendarView(CalendarMonthView):
    template_name = "extra_views/event_calendar_month.html"
    model = Event
    month_format = "%b"
    date_field = "date"


class SearchableItemListView(SearchableListMixin, generic.ListView):
    template_name = "extra_views/item_list.html"
    search_fields = ["name", "sku"]
    search_date_fields = ["date_placed"]
    model = Item
    define_query = False
    exact_query = False
    wrong_lookup = False

    def get_search_query(self):
        if self.define_query:
            return "test B"
        else:
            return super().get_search_query()

    def get(self, request, *args, **kwargs):
        if self.exact_query:
            self.search_fields = [("name", "iexact"), "sku"]
        elif self.wrong_lookup:
            self.search_fields = [("name", "gte"), "sku"]
        return super().get(request, *args, **kwargs)


class SortableItemListView(SortableListMixin, generic.ListView):
    template_name = "extra_views/sortable_item_list.html"
    sort_fields = ["name", "sku"]
    model = Item

    def get(self, request, *args, **kwargs):
        if kwargs["flag"] == "fields_and_aliases":
            self.sort_fields_aliases = [("name", "by_name"), ("sku", "by_sku")]
        elif kwargs["flag"] == "aliases":
            self.sort_fields_aliases = [("name", "by_name"), ("sku", "by_sku")]
            self.sort_fields = []
        return super().get(request, *args, **kwargs)
