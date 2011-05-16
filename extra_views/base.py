from django.views.generic.base import TemplateResponseMixin, View
from django.http import HttpResponseRedirect

class FormsetMixin(object):
    initial = {}
    formset_class = None
    success_url = None

    def get_initial(self):
      return self.initial

    def get_formset_class(self):
        return self.formset_class

    def get_formset(self):
        pass

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

    def formset_valid(self, formset):
        return HttpResponseRedirect(self.get_success_url())

    def formset_invalid(self, formset):
        return self.render_to_response(self.get_context_data(formset=formset))


class ProcessFormsetView(View):
    """
    A mixin that processes a fomset on POST.
    """
    def get(self, request, *args, **kwargs):
        formset_class = self.get_formset_class()
        formset = self.get_form(formset_class)
        return self.render_to_response(self.get_context_data(formset=formset))

    def post(self, request, *args, **kwargs):
        formset_class = self.get_formset_class()
        formset = self.get_formset(formset_class)
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

class FormsetView(TemplateResponseMixin, BaseFormView):
    """
    A view for displaying a form, and rendering a template response
    """

