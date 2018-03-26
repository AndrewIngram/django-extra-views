import django
from django.views.generic.base import TemplateResponseMixin, View, ContextMixin
from django.http import HttpResponseRedirect
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory, inlineformset_factory
from django.views.generic.detail import SingleObjectMixin, SingleObjectTemplateResponseMixin
from django.views.generic.list import MultipleObjectMixin, MultipleObjectTemplateResponseMixin
from django.forms.models import BaseInlineFormSet


class BaseFormSetMixin(object):
    """
    Base class for constructing a FormSet within a view
    """

    initial = []
    form_class = None
    formset_class = None
    success_url = None
    prefix = None
    formset_kwargs = {}
    factory_kwargs = {}

    def construct_formset(self):
        """
        Returns an instance of the formset
        """
        formset_class = self.get_formset()
        if hasattr(self, 'get_extra_form_kwargs'):
            klass = type(self).__name__
            raise DeprecationWarning(
                'Calling {0}.get_extra_form_kwargs is no longer supported. '
                'Set `form_kwargs` in {0}.formset_kwargs or override '
                '{0}.get_formset_kwargs() directly.'.format(klass),
            )
        return formset_class(**self.get_formset_kwargs())

    def get_initial(self):
        """
        Returns a copy of the initial data to use for formsets on this view.
        """
        return self.initial[:]

    def get_prefix(self):
        """
        Returns the prefix used for formsets on this view.
        """
        return self.prefix

    def get_formset_class(self):
        """
        Returns the formset class to use in the formset factory
        """
        return self.formset_class

    def get_form_class(self):
        """
        Returns the form class to use with the formset in this view
        """
        return self.form_class

    def get_formset(self):
        """
        Returns the formset class from the formset factory
        """
        return formset_factory(self.get_form_class(), **self.get_factory_kwargs())

    def get_formset_kwargs(self):
        """
        Returns the keyword arguments for instantiating the formset.
        """
        kwargs = self.formset_kwargs.copy()
        kwargs.update({
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        })

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST.copy(),
                'files': self.request.FILES,
            })
        return kwargs

    def get_factory_kwargs(self):
        """
        Returns the keyword arguments for calling the formset factory
        """
        # Perform deprecation check
        for attr in ['extra', 'max_num', 'can_order', 'can_delete', 'ct_field',
                     'formfield_callback', 'fk_name', 'widgets', 'ct_fk_field']:
            if hasattr(self, attr):
                klass = type(self).__name__
                raise DeprecationWarning(
                    'Setting `{0}.{1}` at the class level is now deprecated. '
                    'Set `{0}.factory_kwargs` instead.'.format(klass, attr)
                )

        kwargs = self.factory_kwargs.copy()
        if self.get_formset_class():
            kwargs['formset'] = self.get_formset_class()
        return kwargs


class FormSetMixin(BaseFormSetMixin, ContextMixin):
    """
    A mixin that provides a way to show and handle a formset in a request.
    """

    def get_success_url(self):
        """
        Returns the supplied URL.
        """
        if self.success_url:
            url = self.success_url
        else:
            # Default to returning to the same page
            url = self.request.get_full_path()
        return url

    def formset_valid(self, formset):
        """
        If the formset is valid redirect to the supplied URL
        """
        return HttpResponseRedirect(self.get_success_url())

    def formset_invalid(self, formset):
        """
        If the formset is invalid, re-render the context data with the
        data-filled formset and errors.
        """
        return self.render_to_response(self.get_context_data(formset=formset))


class ModelFormSetMixin(FormSetMixin, MultipleObjectMixin):
    """
    A mixin that provides a way to show and handle a model formset in a request.
    """

    exclude = None
    fields = None

    def get_context_data(self, **kwargs):
        """
        If an object list has been supplied, inject it into the context with the
        supplied context_object_name name.
        """
        context = {}

        if self.object_list is not None:
            context['object_list'] = self.object_list
            context_object_name = self.get_context_object_name(self.object_list)
            if context_object_name:
                context[context_object_name] = self.object_list
        context.update(kwargs)

        # MultipleObjectMixin get_context_data() doesn't work when object_list
        # is not provided in kwargs, so we skip MultipleObjectMixin and call
        # ContextMixin directly.
        return ContextMixin.get_context_data(self, **context)

    def get_formset_kwargs(self):
        """
        Returns the keyword arguments for instantiating the formset.
        """
        kwargs = super(ModelFormSetMixin, self).get_formset_kwargs()
        kwargs['queryset'] = self.get_queryset()
        return kwargs

    def get_factory_kwargs(self):
        """
        Returns the keyword arguments for calling the formset factory
        """
        kwargs = super(ModelFormSetMixin, self).get_factory_kwargs()
        kwargs.setdefault('fields', self.fields)
        kwargs.setdefault('exclude', self.exclude)

        if self.get_form_class():
            kwargs['form'] = self.get_form_class()
        if self.get_formset_class():
            kwargs['formset'] = self.get_formset_class()
        return kwargs

    def get_formset(self):
        """
        Returns the formset class from the model formset factory
        """
        return modelformset_factory(self.model, **self.get_factory_kwargs())

    def formset_valid(self, formset):
        """
        If the formset is valid, save the associated models.
        """
        self.object_list = formset.save()
        return super(ModelFormSetMixin, self).formset_valid(formset)


class BaseInlineFormSetMixin(BaseFormSetMixin):
    """
    Base class for constructing an inline formSet within a view
    """
    model = None
    inline_model = None
    formset_class = BaseInlineFormSet
    exclude = None
    fields = None

    def get_context_data(self, **kwargs):
        """
        If an object has been supplied, inject it into the context with the
        supplied context_object_name name.
        """
        context = {}

        if self.object:
            context['object'] = self.object
            context_object_name = self.get_context_object_name(self.object)
            if context_object_name:
                context[context_object_name] = self.object
        context.update(kwargs)
        return super(BaseInlineFormSetMixin, self).get_context_data(**context)

    def get_inline_model(self):
        """
        Returns the inline model to use with the inline formset
        """
        return self.inline_model

    def get_formset_kwargs(self):
        """
        Returns the keyword arguments for instantiating the formset.
        """
        # Perform deprecation check
        if hasattr(self, 'save_as_new'):
            klass = type(self).__name__
            raise DeprecationWarning(
                'Setting `{0}.save_as_new` at the class level is now '
                'deprecated. Set `{0}.formset_kwargs` instead.'.format(klass)
            )
        kwargs = super(BaseInlineFormSetMixin, self).get_formset_kwargs()
        kwargs['instance'] = self.object
        return kwargs

    def get_factory_kwargs(self):
        """
        Returns the keyword arguments for calling the formset factory
        """
        kwargs = super(BaseInlineFormSetMixin, self).get_factory_kwargs()
        kwargs.setdefault('fields', self.fields)
        kwargs.setdefault('exclude', self.exclude)

        if self.get_form_class():
            kwargs['form'] = self.get_form_class()
        if self.get_formset_class():
            kwargs['formset'] = self.get_formset_class()
        return kwargs

    def get_formset(self):
        """
        Returns the formset class from the inline formset factory
        """
        return inlineformset_factory(self.model, self.get_inline_model(), **self.get_factory_kwargs())


class InlineFormSetMixin(BaseInlineFormSetMixin, FormSetMixin, SingleObjectMixin):
    """
    A mixin that provides a way to show and handle a inline formset in a request.
    """

    def formset_valid(self, formset):
        self.object_list = formset.save()
        return super(InlineFormSetMixin, self).formset_valid(formset)


class ProcessFormSetView(View):
    """
    A mixin that processes a formset on POST.
    """

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates a blank version of the formset.
        """
        formset = self.construct_formset()
        return self.render_to_response(self.get_context_data(formset=formset))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a formset instance with the passed
        POST variables and then checked for validity.
        """
        formset = self.construct_formset()
        if formset.is_valid():
            return self.formset_valid(formset)
        else:
            return self.formset_invalid(formset)

    # PUT is a valid HTTP verb for creating (with a known URL) or editing an
    # object, note that browsers only support POST for now.
    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)


class BaseFormSetView(FormSetMixin, ProcessFormSetView):
    """
    A base view for displaying a formset
    """


class FormSetView(TemplateResponseMixin, BaseFormSetView):
    """
    A view for displaying a formset, and rendering a template response
    """


class BaseModelFormSetView(ModelFormSetMixin, ProcessFormSetView):
    """
    A base view for displaying a model formset
    """
    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return super(BaseModelFormSetView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return super(BaseModelFormSetView, self).post(request, *args, **kwargs)


class ModelFormSetView(MultipleObjectTemplateResponseMixin, BaseModelFormSetView):
    """
    A view for displaying a model formset, and rendering a template response
    """


class BaseInlineFormSetView(InlineFormSetMixin, ProcessFormSetView):
    """
    A base view for displaying an inline formset for a queryset belonging to a parent model
    """
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(BaseInlineFormSetView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(BaseInlineFormSetView, self).post(request, *args, **kwargs)


class InlineFormSetView(SingleObjectTemplateResponseMixin, BaseInlineFormSetView):
    """
    A view for displaying an inline formset for a queryset belonging to a parent model
    """
