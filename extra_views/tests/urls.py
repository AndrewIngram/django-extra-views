from django.conf.urls.defaults import patterns
from django.views.generic import TemplateView
from formsets import AddressFormSet
from views import AddressFormsetView, ItemModelFormsetView, OrderAndAddressView

urlpatterns = patterns('',
    (r'^formset/simple/$', AddressFormsetView.as_view()),
    (r'^formset/simple_redirect/$', AddressFormsetView.as_view(success_url="/formset/simple_redirect/valid/")),
    (r'^formset/simple_redirect/valid/$', TemplateView.as_view(template_name='extra_views/success.html')),
    (r'^formset/custom/$', AddressFormsetView.as_view(formset_class=AddressFormSet)),
    (r'^modelformset/simple/$', ItemModelFormsetView.as_view()),
    (r'^multiview/simple/$', OrderAndAddressView.as_view()),   
)