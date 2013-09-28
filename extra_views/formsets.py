from django.contrib.contenttypes.generic import generic_inlineformset_factory
from django.contrib.contenttypes.generic import BaseGenericInlineFormSet
from django.forms.formsets import formset_factory
from django.forms.formsets import BaseFormSet
from django.forms.models import modelformset_factory, inlineformset_factory
from django.forms.models import BaseModelFormSet, BaseInlineFormSet
from django.utils.functional import curry


class BaseFormSetMixin(object):
    """
    A base class for declaritive style formset definitions.

    Used by each of the following:

    * FormSetMixin
    * ModelFormSetMixin
    * InlineFormSetMixin
    * GenericInlineFormSetMixin
    """
    formset_context_name = None

    def get_context_data(self, **kwargs):
        """
        If `inlines_names` has been defined, add each formset to the context
        under its corresponding entry in `inlines_names`.
        """
        if self.formset_context_name and 'formset' in kwargs:
            kwargs[self.formset_context_name] = kwargs['formset']
        return super(BaseFormSetMixin, self).get_context_data(**kwargs)

    def formset_factory(self):
        """
        Subclasses must override this method to determine how the formset
        class is created.
        """
        raise NotImplemented('formset_factory() must be implemented')

    def get_extra_form_kwargs(self):
        """
        Override this method to provide extra keyword arguments to each form
        within the formset.
        """
        return {}

    def get_formset(self, data=None, files=None, **kwargs):
        """
        Returns an instantiated formset.

        This is analgous to django-vanilla-views's `get_form()` method.
        """
        formset_class = self.formset_factory()

        # Hack to let as pass additional kwargs to each forms constructor. Be aware that this
        # doesn't let us provide *different* arguments for each form
        extra_form_kwargs = self.get_extra_form_kwargs()
        if extra_form_kwargs:
            formset_class.form = staticmethod(curry(formset_class.form, **extra_form_kwargs))

        return formset_class(data=data, files=files, **kwargs)


class FormSetMixin(BaseFormSetMixin):
    """
    Mixin class for constructing a formset.
    """
    formset_class = BaseFormSet
    form_class = None

    extra = 2
    max_num = None
    can_order = False
    can_delete = False

    def formset_factory(self):
        kwargs = {
            'formset': self.formset_class,
            'extra': self.extra,
            'max_num': self.max_num,
            'can_order': self.can_order,
            'can_delete': self.can_delete
        }
        return formset_factory(self.form_class, **kwargs)


class ModelFormSetMixin(BaseFormSetMixin):
    """
    Mixin class for constructing a model formset.
    """
    formset_class = BaseModelFormSet
    form_class = None

    extra = 2
    max_num = None
    can_order = False
    can_delete = False

    model = None
    fields = None
    exclude = None
    formfield_callback = None

    def formset_factory(self):
        kwargs = {
            'formset': self.formset_class,
            'extra': self.extra,
            'max_num': self.max_num,
            'can_order': self.can_order,
            'can_delete': self.can_delete,
            'fields': self.fields,
            'exclude': self.exclude,
            'formfield_callback': self.formfield_callback
        }
        if self.form_class:
            kwargs['form'] = self.form_class
        return modelformset_factory(self.model, **kwargs)


class InlineFormSetMixin(BaseFormSetMixin):
    """
    Mixin class for constructing an inline formset.
    """
    formset_class = BaseInlineFormSet
    form_class = None

    extra = 2
    max_num = None
    can_order = False
    can_delete = True

    model = None
    fields = None
    exclude = None
    formfield_callback = None

    inline_model = None
    fk_name = None

    def formset_factory(self):
        """
        Returns the keyword arguments for calling the formset factory
        """
        kwargs = {
            'formset': self.formset_class,
            'extra': self.extra,
            'max_num': self.max_num,
            'can_order': self.can_order,
            'can_delete': self.can_delete,
            'fields': self.fields,
            'exclude': self.exclude,
            'formfield_callback': self.formfield_callback,
            'fk_name': self.fk_name
        }
        if self.form_class:
            kwargs['form'] = self.form_class
        return inlineformset_factory(self.model, self.inline_model, **kwargs)


class GenericInlineFormSetMixin(BaseFormSetMixin):
    """
    Mixin class for constructing an generic inline formset.
    """
    formset_class = BaseGenericInlineFormSet

    extra = 2
    max_num = None
    can_order = False
    can_delete = True

    model = None
    fields = None
    exclude = None
    form_class = None
    formfield_callback = None

    inline_model = None
    ct_field = 'content_type'
    ct_fk_field = 'object_id'

    def formset_factory(self):
        """
        Returns the keyword arguments for calling the formset factory
        """
        kwargs = {
            'formset': self.formset_class,
            'extra': self.extra,
            'max_num': self.max_num,
            'can_order': self.can_order,
            'can_delete': self.can_delete,
            'exclude': self.exclude,
            'fields': self.fields,
            'formfield_callback': self.formfield_callback,
            'ct_field': self.ct_field,
            'fk_field': self.ct_fk_field,
        }
        if self.form_class:
            kwargs['form'] = self.form_class
        return generic_inlineformset_factory(self.inline_model, **kwargs)


# The following classes are used for declaring inline formsets.
# Note that these are regular classes, not views.

class InlineFormSet(InlineFormSetMixin):
    """
    An class that provides a way to handle inline formsets within a view.
    """

    def __init__(self, parent_model):
        self.inline_model = self.model
        self.model = parent_model


class GenericInlineFormSet(GenericInlineFormSetMixin):
    """
    An class that provides a way to handle generic inline formsets within a view.
    """

    def __init__(self, parent_model):
        self.inline_model = self.model
        self.model = parent_model
