from django.views.generic.base import TemplateResponseMixin, View
from django.http import HttpResponseRedirect
from django.forms.formsets import formset_factory

class FormsetMixin(object):
    initial = {}
    form_class = None
    formset_class = None  # Sometimes used if we want validation on the overall formset
    success_url = None
    extra = 2
    max_num = 1
    can_order = False
    can_delete = False

    def get_initial(self):
        return self.initial

    def get_formset_class(self):
        return self.formset_class

    def get_form_class(self):
        return self.form_class

    def get_formset(self):
        return formset_factory(self.get_form_class(), formset=self.get_formset_class(), extra=self.extra, max_num=self.max_num, can_order=self.can_order, can_delete=self.can_delete)

    def get_formset_kwargs(self):
        kwargs = {'initial': self.get_initial()}
        return kwargs

    def get_context_data(self, **kwargs):
        return kwargs

    def get_success_url(self):
        if self.success_url:
            url = self.success_url
        else:
            # Default to returning to the same page
            url = self.request.get_full_path() 
        return url

    def formset_valid(self, formset):
        return HttpResponseRedirect(self.get_success_url())

    def formset_invalid(self, formset):
        return self.render_to_response(self.get_context_data(formset=formset))


class ProcessFormsetView(View):
    """
    A mixin that processes a fomset on POST.
    """
    def get(self, request, *args, **kwargs):
        formset = self.get_formset()(initial=self.get_initial())
        return self.render_to_response(self.get_context_data(formset=formset))

    def post(self, request, *args, **kwargs):
        formset = self.get_formset()(request.POST, request.FILES, initial=self.get_initial())
        if formset.is_valid():
            return self.formset_valid(formset)
        else:
            return self.formset_invalid(formset)

    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)


class BaseFormsetView(FormsetMixin, ProcessFormsetView):
    """
    A base view for displaying a formset
    """


class FormsetView(TemplateResponseMixin, BaseFormsetView):
    """
    A view for displaying a form, and rendering a template response
    """

