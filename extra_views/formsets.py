from django.views.generic.base import TemplateResponseMixin, View
from django.http import HttpResponseRedirect
from django.forms.formsets import formset_factory, BaseFormSet
from django.forms.models import BaseModelFormSet
from django.forms.models import modelformset_factory, inlineformset_factory
from django.template.response import TemplateResponse
from django.forms.models import BaseInlineFormSet
from django.utils.functional import curry
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
        formset_class = formset_factory(self.form_class, **factory_kwargs)

        # Hack to let as pass additional kwargs to each forms constructor. Be aware that this
        # doesn't let us provide *different* arguments for each form
        extra_form_kwargs = self.get_extra_form_kwargs()
        if extra_form_kwargs:
            formset_class.form = staticmethod(curry(formset_class.form, **extra_form_kwargs))

        return formset_class(data=data, files=files, **kwargs)


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
        formset_class = modelformset_factory(self.model, **factory_kwargs)

        # Hack to let as pass additional kwargs to each forms constructor. Be aware that this
        # doesn't let us provide *different* arguments for each form
        extra_form_kwargs = self.get_extra_form_kwargs()
        if extra_form_kwargs:
            formset_class.form = staticmethod(curry(formset_class.form, **extra_form_kwargs))

        return formset_class(data=data, files=files, **kwargs)


class GenericInlineFormSetView(GenericModelView):
    """
    Base class for constructing an inline formset within a view
    """
    formset_class = BaseInlineFormSet
    model = None
    inline_model = None
    fk_name = None
    form_class = None
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
        if self.form_class:
            kwargs['form'] = self.form_class
        return kwargs

    def get_formset(self, data=None, files=None, **kwargs):
        """
        Returns an instance of the formset
        """
        factory_kwargs = self.get_factory_kwargs()
        formset_class = inlineformset_factory(self.model, self.inline_model, **factory_kwargs)

        # Hack to let as pass additional kwargs to each forms constructor. Be aware that this
        # doesn't let us provide *different* arguments for each form
        extra_form_kwargs = self.get_extra_form_kwargs()
        if extra_form_kwargs:
            formset_class.form = staticmethod(curry(formset_class.form, **extra_form_kwargs))

        return formset_class(data=data, files=files, **kwargs)


### Concrete view classes

class FormSetView(GenericFormSetView):
    success_url = None

    def get(self, request, *args, **kwargs):
        """
        Display a formset.
        """
        formset = self.get_formset()
        context = self.get_context_data(formset=formset)
        return self.render_to_response(context)

    def post(self, request):
        """
        Attempt to save the formset, and either redisplay with errors,
        or save and redirect.
        """
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
        """
        Display a list of objects and formset.
        """
        self.object_list = self.get_queryset()
        formset = self.get_formset()
        context = self.get_context_data(formset=formset)
        return self.render_to_response(context)

    def post(self, request):
        """
        Attempt to save the formset, and either redisplay with errors,
        or save and redirect.
        """
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


class InlineFormSetView(GenericInlineFormSetView):
    success_url = None

    def get(self, request, *args, **kwargs):
        """
        Display an object and a formset for it.
        """
        self.object = self.get_object()
        formset = self.get_formset(instance=self.object)
        context = self.get_context_data(formset=formset)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """
        Attempt to save the formset, and either redisplay with errors,
        or save and redirect.
        """
        self.object = self.get_object()
        formset = self.get_formset(data=request.POST, files=request.FILES, instance=self.object)
        if formset.is_valid():
            return self.formset_valid(formset)
        else:
            return self.formset_invalid(formset)

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        return self.request.get_full_path()

    def formset_valid(self, formset):
        self.object_list = formset.save()
        return HttpResponseRedirect(self.get_success_url())

    def formset_invalid(self, formset):
        context = self.get_context_data(formset=formset)
        return self.render_to_response(context)