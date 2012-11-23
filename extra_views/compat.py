# ContextMixin was introduced in Django 1.5, we provide a copy for earlier
# versions.
try:
    from django.views.generic.base import ContextMixin
except ImportError:
    class ContextMixin(object):
        """
        A default context mixin that passes the keyword arguments received by
        get_context_data as the template context.
        """

        def get_context_data(self, **kwargs):
            if 'view' not in kwargs:
                kwargs['view'] = self
            return kwargs
