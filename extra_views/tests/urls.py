from django.conf.urls.defaults import *
from views import AddressFormsetView

urlpatterns = patterns('',
    (r'^formset/simple/$', AddressFormsetView.as_view()),
)