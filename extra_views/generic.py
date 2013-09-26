from django.contrib.contenttypes.generic import generic_inlineformset_factory, BaseGenericInlineFormSet
from extra_views.formsets import GenericInlineFormSetView, InlineFormSetView


class BaseGenericInlineFormSetMixin(GenericInlineFormSetView):
    """
    Base class for constructing an generic inline formset within a view
    """

    ct_field = "content_type"
    ct_fk_field = "object_id"
    formset_class = BaseGenericInlineFormSet

    def get_factory_kwargs(self):
        """
        Returns the keyword arguments for calling the formset factory
        """
        kwargs = super(BaseGenericInlineFormSetMixin, self).get_factory_kwargs()
        del kwargs['fk_name']
        kwargs.update({
            "ct_field": self.ct_field,
            "fk_field": self.ct_fk_field,
        })
        return kwargs

    def construct_formset(self):
        """
        Returns an instance of the formset
        """
        factory_kwargs = self.get_factory_kwargs()
        formset_class = generic_inlineformset_factory(self.inline_model, **factory_kwargs)

        # Hack to let as pass additional kwargs to each forms constructor. Be aware that this
        # doesn't let us provide *different* arguments for each form
        extra_form_kwargs = self.get_extra_form_kwargs()
        if extra_form_kwargs:
            formset_class.form = staticmethod(curry(formset_class.form, **extra_form_kwargs))

        return formset_class(**self.get_formset_kwargs())


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


class GenericInlineFormSetView(BaseGenericInlineFormSetMixin, InlineFormSetView):
    """
    A view for displaying a generic inline formset for a queryset belonging to a parent model
    """
