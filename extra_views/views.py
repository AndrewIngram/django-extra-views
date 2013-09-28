from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from extra_views.formsets import FormSetMixin, ModelFormSetMixin
from extra_views.formsets import InlineFormSetMixin, GenericInlineFormSetMixin
from vanilla import GenericView, GenericModelView


class FormSetView(FormSetMixin, GenericView):
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


class ModelFormSetView(ModelFormSetMixin, GenericModelView):
    success_url = None

    def get(self, request, *args, **kwargs):
        """
        Display a list of objects and formset.
        """
        self.object_list = self.get_queryset()
        formset = self.get_formset(queryset=self.object_list)
        context = self.get_context_data(formset=formset)
        return self.render_to_response(context)

    def post(self, request):
        """
        Attempt to save the formset, and either redisplay with errors,
        or save and redirect.
        """
        self.object_list = self.get_queryset()
        formset = self.get_formset(data=request.POST, files=request.FILES, queryset=self.object_list)
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


class InlineFormSetView(InlineFormSetMixin, GenericModelView):
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

    def formset_valid(self, formset):
        self.object_list = formset.save()
        return HttpResponseRedirect(self.get_success_url())

    def formset_invalid(self, formset):
        context = self.get_context_data(formset=formset)
        return self.render_to_response(context)

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        return self.request.get_full_path()


class GenericInlineFormSetView(GenericInlineFormSetMixin, InlineFormSetView):
    """
    Exactly the same as `InlineFormSetView` except that we override
    `InlineFormSetMixin` with `GenericInlineFormSetMixin`.
    """
    pass
