from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory, modelformset_factory
from django.http import HttpResponseRedirect
from django.views.generic.base import ContextMixin, TemplateResponseMixin, View
from django.views.generic.detail import (
    SingleObjectMixin,
    SingleObjectTemplateResponseMixin,
)
from django.views.generic.list import (
    MultipleObjectMixin,
    MultipleObjectTemplateResponseMixin,
)


class BaseFormSetFactory(object):
    """
    Base class for constructing a FormSet from `formset_factory` in a view.

    Calling `construct_formset` calls all other methods.
    """

    initial = []
    form_class = None
    formset_class = None
    prefix = None
    formset_kwargs = {}
    factory_kwargs = {}

    def construct_formset(self):
        """
        Returns an instance of the formset
        """
        formset_class = self.get_formset()
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
        kwargs.update({"initial": self.get_initial(), "prefix": self.get_prefix()})

        if self.request.method in ("POST", "PUT"):
            kwargs.update(
                {"data": self.request.POST.copy(), "files": self.request.FILES}
            )
        return kwargs

    def get_factory_kwargs(self):
        """
        Returns the keyword arguments for calling the formset factory
        """
        kwargs = self.factory_kwargs.copy()
        if self.get_formset_class():
            kwargs["formset"] = self.get_formset_class()
        return kwargs


class FormSetMixin(BaseFormSetFactory, ContextMixin):
    """
    A view mixin that provides a way to show and handle a single formset in a request.
    """

    success_url = None

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
    A view mixin that provides a way to show and handle a single model formset
    in a request.

    Uses `modelformset_factory`.
    """

    exclude = None
    fields = None

    def get_factory_kwargs(self):
        """
        Returns the keyword arguments for calling the formset factory
        """
        kwargs = super().get_factory_kwargs()
        kwargs.setdefault("fields", self.fields)
        kwargs.setdefault("exclude", self.exclude)

        if self.get_form_class():
            kwargs["form"] = self.get_form_class()
        return kwargs

    def get_formset(self):
        """
        Returns the formset class from the model formset factory
        """
        return modelformset_factory(self.model, **self.get_factory_kwargs())

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        formset_class = self.get_formset()
        formset_kwargs = self.get_formset_kwargs()
        formset_kwargs["queryset"] = context['object_list']
        context['formset'] = formset_class(**formset_kwargs)
        return context

    def formset_valid(self, formset):
        """
        If the formset is valid, save the associated models.
        """
        self.object_list = formset.save()
        return super().formset_valid(formset)


class BaseInlineFormSetFactory(BaseFormSetFactory):
    """
    Base class for constructing a FormSet from `inlineformset_factory` in a view.

    Calling `construct_formset` calls all other methods.
    """

    model = None
    inline_model = None
    exclude = None
    fields = None

    def get_inline_model(self):
        """
        Returns the inline model to use with the inline formset
        """
        return self.inline_model

    def get_formset_kwargs(self):
        """
        Returns the keyword arguments for instantiating the formset.
        """
        kwargs = super().get_formset_kwargs()
        kwargs["instance"] = self.object
        return kwargs

    def get_factory_kwargs(self):
        """
        Returns the keyword arguments for calling the formset factory
        """
        kwargs = super().get_factory_kwargs()
        kwargs.setdefault("fields", self.fields)
        kwargs.setdefault("exclude", self.exclude)

        if self.get_form_class():
            kwargs["form"] = self.get_form_class()
        return kwargs

    def get_formset(self):
        """
        Returns the formset class from the inline formset factory
        """
        return inlineformset_factory(
            self.model, self.get_inline_model(), **self.get_factory_kwargs()
        )


class InlineFormSetMixin(BaseInlineFormSetFactory, SingleObjectMixin, FormSetMixin):
    """
    A view mixin that provides a way to show and handle a single inline formset
    in a request.
    """

    def formset_valid(self, formset):
        self.object_list = formset.save()
        return super().formset_valid(formset)


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
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return super().post(request, *args, **kwargs)


class ModelFormSetView(MultipleObjectTemplateResponseMixin, BaseModelFormSetView):
    """
    A view for displaying a model formset, and rendering a template response
    """


class BaseInlineFormSetView(InlineFormSetMixin, ProcessFormSetView):
    """
    A base view for displaying an inline formset for a queryset belonging to
    a parent model
    """

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)


class InlineFormSetView(SingleObjectTemplateResponseMixin, BaseInlineFormSetView):
    """
    A view for displaying an inline formset for a queryset belonging to a parent model
    """
