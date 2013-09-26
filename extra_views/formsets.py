from django.views.generic.base import TemplateResponseMixin, View
from django.http import HttpResponseRedirect
from django.forms.formsets import formset_factory, BaseFormSet
from django.forms.models import BaseModelFormSet
from django.forms.models import modelformset_factory, inlineformset_factory
from django.template.response import TemplateResponse
from django.views.generic.detail import SingleObjectMixin, SingleObjectTemplateResponseMixin
from django.views.generic.list import MultipleObjectMixin, MultipleObjectTemplateResponseMixin
from django.forms.models import BaseInlineFormSet
from django.utils.functional import curry
from .compat import ContextMixin
from vanilla import GenericView, GenericModelView


########## Vanilla style ##########

class GenericFormSetView(GenericView):
    """
    A generic base class for building formset views.
    """
    formset_class = BaseFormSet
    extra = 2
    max_num = None
    can_order = False
    can_delete = False

    def get_factory_kwargs(self):
        return {
            'extra': self.extra,
            'max_num': self.max_num,
            'can_order': self.can_order,
            'can_delete': self.can_delete,
            'formset': self.formset_class
        }

    def get_extra_form_kwargs(self):
        return {}

    def get_formset(self, data=None, files=None, **kwargs):
        """
        Returns the formset class from the formset factory
        """
        factory_kwargs = self.get_factory_kwargs()
        formset_cls = formset_factory(self.get_form_class(), **factory_kwargs)

        extra_form_kwargs = self.get_extra_form_kwargs()
        # Hack to let as pass additional kwargs to each forms constructor. Be aware that this
        # doesn't let us provide *different* arguments for each form
        if extra_form_kwargs:
            formset_cls.form = staticmethod(curry(formset_cls.form, **extra_form_kwargs))

        return formset_cls(data=data, files=files, **kwargs)


class GenericModelFormSetView(GenericModelView):
    """
    A generic base class for building model formset views.
    """
    formset_class = BaseModelFormSet
    extra = 2
    max_num = None
    can_order = False
    can_delete = False
    fields = None
    exclude = None
    formfield_callback = None

    def get_factory_kwargs(self):
        ret = {
            'extra': self.extra,
            'max_num': self.max_num,
            'can_order': self.can_order,
            'can_delete': self.can_delete,
            'fields': self.fields,
            'exclude': self.exclude,
            'formset': self.formset_class,
            'formfield_callback': self.formfield_callback
        }
        if self.form_class:
            ret['form'] = self.form_class
        return ret

    def get_extra_form_kwargs(self):
        return {}

    def get_formset(self, data=None, files=None, **kwargs):
        """
        Returns the formset class from the formset factory
        """
        factory_kwargs = self.get_factory_kwargs()
        formset_cls = modelformset_factory(self.model, **factory_kwargs)

        extra_form_kwargs = self.get_extra_form_kwargs()
        # Hack to let as pass additional kwargs to each forms constructor. Be aware that this
        # doesn't let us provide *different* arguments for each form
        if extra_form_kwargs:
            formset_cls.form = staticmethod(curry(formset_cls.form, **extra_form_kwargs))

        return formset_cls(data=data, files=files, queryset=self.get_queryset(), **kwargs)



class FormSetView(GenericFormSetView):
    success_url = None

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        context = self.get_context_data(formset=formset)
        return self.render_to_response(context)

    def post(self, request):
        formset = self.get_formset(data=request.POST, files=request.FILES)
        if formset.is_valid():
            return self.formset_valid(formset)
        return self.formset_invalid(formset)

    def formset_valid(self, formset):
        return HttpResponseRedirect(self.get_success_url())

    def formset_invalid(self, formset):
        context = self.get_context_data(formset=formset)
        return self.render_to_response(context)

    def get_success_url(self):
        if self.success_url is None:
            return self.request.get_full_path()
        return self.success_url


class ModelFormSetView(GenericModelFormSetView):
    success_url = None

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        formset = self.get_formset()
        context = self.get_context_data(formset=formset)
        return self.render_to_response(context)

    def post(self, request):
        self.object_list = self.get_queryset()
        formset = self.get_formset(data=request.POST, files=request.FILES)
        if formset.is_valid():
            return self.formset_valid(formset)
        return self.formset_invalid(formset)

    def formset_valid(self, formset):
        self.object_list = formset.save()
        return HttpResponseRedirect(self.get_success_url())

    def formset_invalid(self, formset):
        context = self.get_context_data(formset=formset)
        return self.render_to_response(context)

    def get_success_url(self):
        if self.success_url is None:
            return self.request.get_full_path()
        return self.success_url


######## oldskool #########


class GenericInlineFormSetView(GenericModelView):
    """
    Base class for constructing an inline formSet within a view
    """
    model = None
    inline_model = None
    fk_name = None
    form_class = None
    formset_class = BaseInlineFormSet
    exclude = None
    fields = None
    formfield_callback = None
    extra = 2
    max_num = None
    can_order = False
    can_delete = True

    def get_extra_form_kwargs(self):
        """
        Returns extra keyword arguments to pass to each form in the formset
        """
        return {}

    def get_formset_kwargs(self):
        """
        Returns the keyword arguments for instantiating the formset.
        """
        kwargs = {}
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })

        kwargs['instance'] = self.object
        return kwargs

    def get_factory_kwargs(self):
        """
        Returns the keyword arguments for calling the formset factory
        """
        kwargs = {
            'extra': self.extra,
            'max_num': self.max_num,
            'can_order': self.can_order,
            'can_delete': self.can_delete,
            'exclude': self.exclude,
            'fields': self.fields,
            'formfield_callback': self.formfield_callback,
            'fk_name': self.fk_name,
            'formset': self.formset_class
        }
        if self.get_form_class():
            kwargs['form'] = self.get_form_class()
        return kwargs

    def get_formset(self):
        """
        Returns the formset class from the inline formset factory
        """
        return inlineformset_factory(self.model, self.inline_model, **self.get_factory_kwargs())

    def construct_formset(self):
        """
        Returns an instance of the formset
        """
        formset_class = self.get_formset()
        extra_form_kwargs = self.get_extra_form_kwargs()

        # Hack to let as pass additional kwargs to each forms constructor. Be aware that this
        # doesn't let us provide *different* arguments for each form
        if extra_form_kwargs:
            formset_class.form = staticmethod(curry(formset_class.form, **extra_form_kwargs))

        return formset_class(**self.get_formset_kwargs())


class InlineFormSetView(GenericInlineFormSetView):
    """
    A base view for displaying an inline formset for a queryset belonging to a parent model
    """
    success_url = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        formset = self.construct_formset()
        return self.render_to_response(self.get_context_data(formset=formset))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        formset = self.construct_formset()
        if formset.is_valid():
            return self.formset_valid(formset)
        else:
            return self.formset_invalid(formset)

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        return self.request.get_full_path()

    def formset_valid(self, formset):
        """
        If the formset is valid, save the objects and redirect.
        """
        self.object_list = formset.save()
        return HttpResponseRedirect(self.get_success_url())

    def formset_invalid(self, formset):
        """
        If the formset is invalid, render the context data with the
        data-filled formset and errors.
        """
        return self.render_to_response(self.get_context_data(formset=formset))