from django.views.generic.edit import FormView, ModelFormMixin
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from extra_views.formsets import GenericInlineFormSetView
from django.http import HttpResponseRedirect
from django.forms.formsets import all_valid
from .compat import ContextMixin
from vanilla import GenericModelView


class InlineFormSet(GenericInlineFormSetView):
    """
    Base class for constructing an inline formset within a view
    """

    def __init__(self, parent_model, request, instance, view_kwargs=None, view=None):
        self.inline_model = self.model
        self.model = parent_model
        self.request = request
        self.object = instance
        self.kwargs = view_kwargs
        self.view = view

    def get_formset(self, data=None, files=None, **kwargs):
        """
        Overrides get_formset to attach the model class as
        an attribute of the returned formset instance.
        """
        formset = super(InlineFormSet, self).get_formset(data=data, files=files, **kwargs)
        formset.model = self.inline_model
        return formset


class ModelWithInlinesView(GenericModelView):
    """
    A mixin that provides a way to show and handle a modelform and inline
    formsets in a request.
    """
    inlines = []

    def get_inlines(self, data=None, files=None, **kwargs):
        """
        Returns the inline formset instances
        """
        instance = kwargs.get('instance', None)
        inline_formsets = []
        for inline_class in self.inlines:
            inline_instance = inline_class(self.model, self.request, instance, self.kwargs, self)
            inline_formset = inline_instance.get_formset(data=data, files=files, **kwargs)
            inline_formsets.append(inline_formset)
        return inline_formsets


class CreateWithInlinesView(ModelWithInlinesView):
    """
    A mixin that renders a form and inline formsets on GET and processes it on POST.
    """
    template_name_suffix = '_form'
    success_url = None

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates a blank version of the form and formsets.
        """
        self.object = None
        form = self.get_form()
        inlines = self.get_inlines()
        context = self.get_context_data(form=form, inlines=inlines)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form and formset instances with the passed
        POST variables and then checked for validity.
        """
        self.object = None
        form = self.get_form(request.POST, request.FILES)

        if form.is_valid():
            self.object = form.save(commit=False)
            inlines = self.get_inlines(request.POST, request.FILES, instance=self.object)
        else:
            inlines = self.get_inlines(request.POST, request.FILES)

        if form.is_valid() and all_valid(inlines):
            return self.forms_valid(form, inlines)
        return self.forms_invalid(form, inlines)

    def forms_valid(self, form, inlines):
        """
        If the form and formsets are valid, save the associated models.
        """
        self.object = form.save()
        for formset in inlines:
            formset.save()
        return HttpResponseRedirect(self.get_success_url())

    def forms_invalid(self, form, inlines):
        """
        If the form or formsets are invalid, re-render the context data with the
        data-filled form and formsets and errors.
        """
        context = self.get_context_data(form=form, inlines=inlines)
        return self.render_to_response(context)


class UpdateWithInlinesView(ModelWithInlinesView):
    """
    A mixin that renders a form and inline formsets on GET and processes it on POST.
    """
    template_name_suffix = '_form'
    success_url = None

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates a blank version of the form and formsets.
        """
        self.object = self.get_object()
        form = self.get_form(instance=self.object)
        inlines = self.get_inlines(instance=self.object)
        context = self.get_context_data(form=form, inlines=inlines)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form and formset instances with the passed
        POST variables and then checked for validity.
        """
        self.object = self.get_object()
        form = self.get_form(request.POST, request.FILES, instance=self.object)

        if form.is_valid():
            self.object = form.save(commit=False)
            inlines = self.get_inlines(request.POST, request.FILES, instance=self.object)
        else:
            inlines = self.get_inlines(request.POST, request.FILES)

        if form.is_valid() and all_valid(inlines):
            return self.forms_valid(form, inlines)
        return self.forms_invalid(form, inlines)

    def forms_valid(self, form, inlines):
        """
        If the form and formsets are valid, save the associated models.
        """
        self.object = form.save()
        for formset in inlines:
            formset.save()
        return HttpResponseRedirect(self.get_success_url())

    def forms_invalid(self, form, inlines):
        """
        If the form or formsets are invalid, re-render the context data with the
        data-filled form and formsets and errors.
        """
        context = self.get_context_data(form=form, inlines=inlines)
        return self.render_to_response(context)



class NamedFormsetsMixin(object):
    """
    A mixin for use with `CreateWithInlinesView` or `UpdateWithInlinesView` that lets
    you define the context variable for each inline.
    """
    inlines_names = []

    def get_inlines_names(self):
        """
        Returns a list of names of context variables for each inline in `inlines`.
        """
        return self.inlines_names

    def get_context_data(self, **kwargs):
        """
        If `inlines_names` has been defined, add each formset to the context under
        its corresponding entry in `inlines_names`
        """
        context = {}
        inlines_names = self.get_inlines_names()

        if inlines_names:
            # We have formset or inlines in context, but never both
            context.update(zip(inlines_names, kwargs.get('inlines', [])))
            if 'formset' in kwargs:
                context[inlines_names[0]] = kwargs['formset']
        context.update(kwargs)
        return super(NamedFormsetsMixin, self).get_context_data(**context)
