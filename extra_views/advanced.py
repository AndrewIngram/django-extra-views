from django.contrib import messages
from django.forms.formsets import all_valid
from django.views.generic.base import ContextMixin
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.views.generic.edit import FormView, ModelFormMixin

from extra_views.formsets import BaseInlineFormSetFactory


class InlineFormSetFactory(BaseInlineFormSetFactory):
    """
    Class used to create an `InlineFormSet` from `inlineformset_factory` as
    one of multiple `InlineFormSet`s within a single view.

    Subclasses `BaseInlineFormSetFactory` and passes in the necessary view arguments.
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
        formset = super().construct_formset()
        formset.model = self.inline_model
        return formset


class ModelFormWithInlinesMixin(ModelFormMixin):
    """
    A mixin that provides a way to show and handle a modelform and inline
    formsets in a request.

    The inlines should be subclasses of `InlineFormSetFactory`.
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
        response = self.form_valid(form)
        for formset in inlines:
            formset.save()
        return response

    def forms_invalid(self, form, inlines):
        """
        If the form or formsets are invalid, re-render the context data with the
        data-filled form and formsets and errors.
        """
        return self.render_to_response(
            self.get_context_data(form=form, inlines=inlines)
        )

    def construct_inlines(self):
        """
        Returns the inline formset instances
        """
        inline_formsets = []
        for inline_class in self.get_inlines():
            inline_instance = inline_class(
                self.model, self.request, self.object, self.kwargs, self
            )
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
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        inlines = self.construct_inlines()
        return self.render_to_response(
            self.get_context_data(form=form, inlines=inlines, **kwargs)
        )

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form and formset instances with the
        passed POST variables and then checked for validity.
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        initial_object = self.object
        if form.is_valid():
            self.object = form.save(commit=False)
            form_validated = True
        else:
            form_validated = False

        inlines = self.construct_inlines()

        if all_valid(inlines) and form_validated:
            return self.forms_valid(form, inlines)
        self.object = initial_object
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
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        return super().post(request, *args, **kwargs)


class CreateWithInlinesView(
    SingleObjectTemplateResponseMixin, BaseCreateWithInlinesView
):
    """
    View for creating a new object instance with related model instances,
    with a response rendered by template.
    """

    template_name_suffix = "_form"


class BaseUpdateWithInlinesView(ModelFormWithInlinesMixin, ProcessFormWithInlinesView):
    """
    Base view for updating an existing object with related model instances.

    Using this base class requires subclassing to provide a response mixin.
    """

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)


class UpdateWithInlinesView(
    SingleObjectTemplateResponseMixin, BaseUpdateWithInlinesView
):
    """
    View for updating an object with related model instances,
    with a response rendered by template.
    """

    template_name_suffix = "_form"


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
            context.update(zip(inlines_names, kwargs.get("inlines", [])))
            if "formset" in kwargs:
                context[inlines_names[0]] = kwargs["formset"]
        context.update(kwargs)
        return super().get_context_data(**context)


class SuccessMessageMixin(object):
    """
    Adds success message on views with inlines if django.contrib.messages framework
    is used.
    In order to use just add mixin in to inheritance before main class, e.g.:
    class MyCreateWithInlinesView (SuccessMessageMixin, CreateWithInlinesView):
        success_message='Something was created!'
    """

    success_message = ""

    def forms_valid(self, form, inlines):
        response = super().forms_valid(form, inlines)
        success_message = self.get_success_message(form.cleaned_data, inlines)
        if success_message:
            messages.success(self.request, success_message)
        return response

    def get_success_message(self, cleaned_data, inlines):
        return self.success_message % cleaned_data


class FormSetSuccessMessageMixin(object):
    """
    Adds success message on FormSet views if django.contrib.messages framework
    is used. In order to use just add mixin in to inheritance before main
    class, e.g.:
    class MyFormSetView (FormSetSuccessMessageMixin, ModelFormSetView):
        success_message='Something was created!'
    """

    success_message = ""

    def formset_valid(self, formset):
        response = super().formset_valid(formset)
        success_message = self.get_success_message(formset)
        if success_message:
            messages.success(self.request, success_message)
        return response

    def get_success_message(self, formset):
        return self.success_message
