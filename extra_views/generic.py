import django
from django.contrib.contenttypes.forms import generic_inlineformset_factory, \
    BaseGenericInlineFormSet

from extra_views.formsets import BaseInlineFormSetMixin, InlineFormSetMixin, \
    BaseInlineFormSetView, InlineFormSetView


class BaseGenericInlineFormSetMixin(BaseInlineFormSetMixin):
    """
    Base class for constructing an generic inline formset within a view
    """
    formset_class = BaseGenericInlineFormSet

    def get_formset(self):
        """
        Returns the final formset class from the inline formset factory
        """
        result = generic_inlineformset_factory(self.inline_model, **self.get_factory_kwargs())
        return result


class GenericInlineFormSet(BaseGenericInlineFormSetMixin):
    """
    An inline class that provides a way to handle generic inline formsets
    """

    def __init__(self, parent_model, request, instance, view_kwargs=None, view=None):
        self.inline_model = self.model
        self.model = parent_model
        self.request = request
        self.object = instance
        self.kwargs = view_kwargs
        self.view = view


class GenericInlineFormSetMixin(BaseGenericInlineFormSetMixin, InlineFormSetMixin):
    """
    A mixin that provides a way to show and handle a generic inline formset in a request.
    """


class BaseGenericInlineFormSetView(GenericInlineFormSetMixin, BaseInlineFormSetView):
    """
    A base view for displaying a generic inline formset
    """


class GenericInlineFormSetView(BaseGenericInlineFormSetView, InlineFormSetView):
    """
    A view for displaying a generic inline formset for a queryset belonging to a parent model
    """
