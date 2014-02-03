from django.conf.urls import patterns
from django.views.generic import TemplateView
from .formsets import AddressFormSet
from .views import AddressFormSetView, AddressFormSetViewNamed, ItemModelFormSetView, \
    FormAndFormSetOverrideView, PagedModelFormSetView, OrderItemFormSetView, \
    OrderCreateView, OrderUpdateView, OrderTagsView, EventCalendarView, OrderCrateNamedView, \
    SortableItemListView, SearchableItemListView

urlpatterns = patterns('',
    (r'^formset/simple/$', AddressFormSetView.as_view()),
    (r'^formset/simple/named/$', AddressFormSetViewNamed.as_view()),
    (r'^formset/simple_redirect/$', AddressFormSetView.as_view(success_url="/formset/simple_redirect/valid/")),
    (r'^formset/simple_redirect/valid/$', TemplateView.as_view(template_name='extra_views/success.html')),
    (r'^formset/custom/$', AddressFormSetView.as_view(formset_class=AddressFormSet)),
    (r'^modelformset/simple/$', ItemModelFormSetView.as_view()),
    (r'^modelformset/custom/$', FormAndFormSetOverrideView.as_view()),
    (r'^modelformset/paged/$', PagedModelFormSetView.as_view()),
    (r'^inlineformset/(?P<pk>\d+)/$', OrderItemFormSetView.as_view()),
    (r'^inlines/new/$', OrderCreateView.as_view()),
    (r'^inlines/new/named/$', OrderCrateNamedView.as_view()),
    (r'^inlines/(?P<pk>\d+)/$', OrderUpdateView.as_view()),
    (r'^genericinlineformset/(?P<pk>\d+)/$', OrderTagsView.as_view()),
    (r'^sortable/(?P<flag>\w+)/$', SortableItemListView.as_view()),
    (r'^events/(?P<year>\d{4})/(?P<month>\w+)/$', EventCalendarView.as_view()),
    (r'^searchable/$', SearchableItemListView.as_view()),
    (r'^searchable/predefined_query/$', SearchableItemListView.as_view(define_query=True)),
    (r'^searchable/exact_query/$', SearchableItemListView.as_view(exact_query=True)),
    (r'^searchable/wrong_lookup/$', SearchableItemListView.as_view(wrong_lookup=True)),
#    (r'^multiview/nosuccess/$', OrderAndAddressView.as_view()),
#    (r'^multiview/simple/$', SimpleMultiView.as_view(success_url="/multiview/simple/valid/")),
#    (r'^multiview/simple/valid/$', TemplateView.as_view(template_name='extra_views/success.html')),
#    (r'^multiview/forms/$', OrderAndAddressView.as_view(success_url="/multiview/forms/valid/")),
#    (r'^multiview/forms/valid/$', TemplateView.as_view(template_name='extra_views/success.html')),
#    (r'^multiview/error/$', InvalidMultiFormView.as_view(success_url="/multiview/error/valid/")),
#    (r'^multiview/error/valid/$', TemplateView.as_view(template_name='extra_views/success.html')),
#    (r'^multiview/formsets/$', OrderAndItemsView.as_view(success_url="/multiview/formsets/valid/")),
#    (r'^multiview/formsets/valid/$', TemplateView.as_view(template_name='extra_views/success.html')),
#    (r'^multiview/handlers/$', MultiViewHandler.as_view(success_url="/multiview/handlers/valid/")),
#    (r'^multiview/handlers/valid/$', TemplateView.as_view(template_name='extra_views/success.html')),
#    (r'^multiview/initialdata/$', MultiViewInitialData.as_view(success_url="/multiview/initialdata/valid/")),
#    (r'^multiview/initialdata/valid/$', TemplateView.as_view(template_name='extra_views/success.html')),
#    (r'^multiview/initialhandler/$', MultiViewInitialHandlers.as_view(success_url="/multiview/initialhandler/valid/")),
#    (r'^multiview/initialhandler/valid/$', TemplateView.as_view(template_name='extra_views/success.html')),
#    (r'^multiview/formsets/$', MultiViewWithFormSets.as_view(success_url="/multiview/formsets/valid/")),
#    (r'^multiview/formsets/valid/$', TemplateView.as_view(template_name='extra_views/success.html')),
)
