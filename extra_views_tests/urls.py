from django.conf.urls import url
from django.views.generic import TemplateView

from .formsets import AddressFormSet
from .views import (
    AddressFormSetView,
    AddressFormSetViewKwargs,
    AddressFormSetViewNamed,
    EventCalendarView,
    FormAndFormSetOverrideView,
    ItemModelFormSetExcludeView,
    ItemModelFormSetView,
    OrderCreateNamedView,
    OrderCreateView,
    OrderItemFormSetView,
    OrderTagsView,
    OrderUpdateView,
    PagedModelFormSetView,
    SearchableItemListView,
    SortableItemListView,
)

urlpatterns = [
    url(r"^formset/simple/$", AddressFormSetView.as_view()),
    url(r"^formset/simple/named/$", AddressFormSetViewNamed.as_view()),
    url(r"^formset/simple/kwargs/$", AddressFormSetViewKwargs.as_view()),
    url(
        r"^formset/simple_redirect/$",
        AddressFormSetView.as_view(success_url="/formset/simple_redirect/valid/"),
    ),
    url(
        r"^formset/simple_redirect/valid/$",
        TemplateView.as_view(template_name="extra_views/success.html"),
    ),
    url(r"^formset/custom/$", AddressFormSetView.as_view(formset_class=AddressFormSet)),
    url(r"^modelformset/simple/$", ItemModelFormSetView.as_view()),
    url(r"^modelformset/exclude/$", ItemModelFormSetExcludeView.as_view()),
    url(r"^modelformset/custom/$", FormAndFormSetOverrideView.as_view()),
    url(r"^modelformset/paged/$", PagedModelFormSetView.as_view()),
    url(r"^inlineformset/(?P<pk>\d+)/$", OrderItemFormSetView.as_view()),
    url(r"^inlines/(\d+)/new/$", OrderCreateView.as_view()),
    url(r"^inlines/new/$", OrderCreateView.as_view()),
    url(r"^inlines/new/named/$", OrderCreateNamedView.as_view()),
    url(r"^inlines/(?P<pk>\d+)/$", OrderUpdateView.as_view()),
    url(r"^genericinlineformset/(?P<pk>\d+)/$", OrderTagsView.as_view()),
    url(r"^sortable/(?P<flag>\w+)/$", SortableItemListView.as_view()),
    url(r"^events/(?P<year>\d{4})/(?P<month>\w+)/$", EventCalendarView.as_view()),
    url(r"^searchable/$", SearchableItemListView.as_view()),
    url(
        r"^searchable/predefined_query/$",
        SearchableItemListView.as_view(define_query=True),
    ),
    url(r"^searchable/exact_query/$", SearchableItemListView.as_view(exact_query=True)),
    url(
        r"^searchable/wrong_lookup/$", SearchableItemListView.as_view(wrong_lookup=True)
    ),
]
