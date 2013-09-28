from django.conf.urls.defaults import patterns
from django.views.generic import TemplateView
from .formsets import AddressFormSet
from .views import AddressFormSetView, AddressFormSetViewNamed, ItemModelFormSetView, \
    FormAndFormSetOverrideView, PagedModelFormSetView, OrderItemFormSetView, \
    OrderCreateView, OrderUpdateView, OrderTagsView, OrderCrateNamedView

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
)
