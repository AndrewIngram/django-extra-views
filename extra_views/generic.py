from django.contrib.contenttypes.forms import generic_inlineformset_factory

from extra_views.formsets import (
    BaseInlineFormSetFactory,
    BaseInlineFormSetView,
    InlineFormSetMixin,
    InlineFormSetView,
)


class BaseGenericInlineFormSetFactory(BaseInlineFormSetFactory):
    """
    Base class for constructing a GenericInlineFormSet from
    `generic_inlineformset_factory` in a view.
    """

    def get_formset(self):
        """
        Returns the final formset class from generic_inlineformset_factory.
        """
        result = generic_inlineformset_factory(
            self.inline_model, **self.get_factory_kwargs()
        )
        return result


class BaseGenericInlineFormSetMixin(BaseGenericInlineFormSetFactory):
    def __init__(self, *args, **kwargs):
        from warnings import warn

        warn(
            "`extra_views.BaseGenericInlineFormSetMixin` has been renamed to "
            "`BaseGenericInlineFormSetFactory`. `BaseGenericInlineFormSetMixin` "
            "will be removed in a future release.",
            DeprecationWarning,
        )
        super(BaseGenericInlineFormSetMixin, self).__init__(*args, **kwargs)


class GenericInlineFormSetFactory(BaseGenericInlineFormSetFactory):
    """
    Class used to create a `GenericInlineFormSet` from `generic_inlineformset_factory`
    as one of multiple `GenericInlineFormSet`s within a single view.

    Subclasses `BaseGenericInlineFormSetFactory` and passes in the necessary view
    arguments.
    """

    def __init__(self, parent_model, request, instance, view_kwargs=None, view=None):
        self.inline_model = self.model
        self.model = parent_model
        self.request = request
        self.object = instance
        self.kwargs = view_kwargs
        self.view = view


class GenericInlineFormSet(GenericInlineFormSetFactory):
    def __init__(self, *args, **kwargs):
        from warnings import warn

        warn(
            "`extra_views.GenericInlineFormSet` has been renamed to "
            "`GenericInlineFormSetFactory`. `GenericInlineFormSet` "
            "will be removed in a future release.",
            DeprecationWarning,
        )
        super(GenericInlineFormSet, self).__init__(*args, **kwargs)


class GenericInlineFormSetMixin(BaseGenericInlineFormSetFactory, InlineFormSetMixin):
    """
    A mixin that provides a way to show and handle a generic inline formset in a
    request.
    """


class BaseGenericInlineFormSetView(GenericInlineFormSetMixin, BaseInlineFormSetView):
    """
    A base view for displaying a generic inline formset
    """


class GenericInlineFormSetView(BaseGenericInlineFormSetView, InlineFormSetView):
    """
    A view for displaying a generic inline formset for a queryset belonging to a
    parent model
    """
