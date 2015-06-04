import django
from django.views.generic.edit import FormView, ModelFormMixin
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from extra_views.formsets import BaseInlineFormSetMixin
from django.http import HttpResponseRedirect
from django.forms.formsets import all_valid
from .compat import ContextMixin


class InlineFormSet(BaseInlineFormSetMixin):
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

    def construct_formset(self):
        """
        Overrides construct_formset to attach the model class as
        an attribute of the returned formset instance.
        """
        formset = super(InlineFormSet, self).construct_formset()
        formset.model = self.inline_model
        return formset


class ModelFormWithInlinesMixin(ModelFormMixin):
    """
    A mixin that provides a way to show and handle a modelform and inline
    formsets in a request.
    """
    inlines = []

    def get_inlines(self):
        """
        Returns the inline formset classes
        """
        return self.inlines

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
        return self.render_to_response(self.get_context_data(form=form, inlines=inlines))

    def construct_inlines(self):
        """
        Returns the inline formset instances
        """
        inline_formsets = []
        for inline_class in self.get_inlines():
            inline_instance = inline_class(self.model, self.request, self.object, self.kwargs, self)
            inline_formset = inline_instance.construct_formset()
            inline_formsets.append(inline_formset)
        return inline_formsets


class ProcessFormWithInlinesView(FormView):
    """
    A mixin that renders a form and inline formsets on GET and processes it on POST.
    """

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates a blank version of the form and formsets.
        """
        if django.VERSION >= (1, 6) and self.fields is None and self.form_class is None:
            self.fields = '__all__'  # backward compatible with older versions

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        inlines = self.construct_inlines()
        return self.render_to_response(self.get_context_data(form=form, inlines=inlines, *args, **kwargs))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form and formset instances with the passed
        POST variables and then checked for validity.
        """
        if django.VERSION >= (1, 6) and self.fields is None and self.form_class is None:
            self.fields = '__all__'  # backward compatible with older versions

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            self.object = form.save(commit=False)
            form_validated = True
        else:
            form_validated = False

        inlines = self.construct_inlines()

        if all_valid(inlines) and form_validated:
            return self.forms_valid(form, inlines)
        return self.forms_invalid(form, inlines)

    # PUT is a valid HTTP verb for creating (with a known URL) or editing an
    # object, note that browsers only support POST for now.
    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)


class BaseCreateWithInlinesView(ModelFormWithInlinesMixin, ProcessFormWithInlinesView):
    """
    Base view for creating an new object instance with related model instances.

    Using this base class requires subclassing to provide a response mixin.
    """

    def get(self, request, *args, **kwargs):
        self.object = None
        return super(BaseCreateWithInlinesView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        return super(BaseCreateWithInlinesView, self).post(request, *args, **kwargs)


class CreateWithInlinesView(SingleObjectTemplateResponseMixin, BaseCreateWithInlinesView):
    """
    View for creating a new object instance with related model instances,
    with a response rendered by template.
    """
    template_name_suffix = '_form'


class BaseUpdateWithInlinesView(ModelFormWithInlinesMixin, ProcessFormWithInlinesView):
    """
    Base view for updating an existing object with related model instances.

    Using this base class requires subclassing to provide a response mixin.
    """

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(BaseUpdateWithInlinesView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(BaseUpdateWithInlinesView, self).post(request, *args, **kwargs)


class UpdateWithInlinesView(SingleObjectTemplateResponseMixin, BaseUpdateWithInlinesView):
    """
    View for updating an object with related model instances,
    with a response rendered by template.
    """
    template_name_suffix = '_form'


class NamedFormsetsMixin(ContextMixin):
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
