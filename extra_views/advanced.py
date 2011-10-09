from django.views.generic.edit import FormView, ModelFormMixin
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from extra_views.formsets import BaseInlineFormSetMixin
from django.http import HttpResponseRedirect
from django.forms.formsets import all_valid 


class InlineFormSet(BaseInlineFormSetMixin):

    def __init__(self, parent_model, request, instance):
        self.inline_model = self.model        
        self.model = parent_model
        self.request = request
        self.object = instance


class ModelFormWithInlinesMixin(ModelFormMixin):
    def forms_valid(self, form, inlines):
        self.object.save()
        form.save_m2m()
        for formset in inlines:
            formset.save()
        return HttpResponseRedirect(self.get_success_url())
    
    def forms_invalid(self, form, inlines):
        return self.render_to_response(self.get_context_data(form=form, inlines=inlines))
    
    def construct_inlines(self):
        inline_formsets = []
        for inline_class in self.inlines:
            inline_instance = inline_class(self.model, self.request, self.object)
            inline_formset = inline_instance.construct_formset()
            inline_formsets.append(inline_formset)
        return inline_formsets


class ProcessFormWithInlinesView(FormView):
    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        inlines = self.construct_inlines()
        return self.render_to_response(self.get_context_data(form=form, inlines=inlines))

    def post(self, request, *args, **kwargs):
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

    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)


class BaseCreateWithInlinesView(ModelFormWithInlinesMixin, ProcessFormWithInlinesView):
    def get(self, request, *args, **kwargs):
        self.object = None
        return super(BaseCreateWithInlinesView, self).get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        self.object = None
        return super(BaseCreateWithInlinesView, self).post(request, *args, **kwargs)


class CreateWithInlinesView(SingleObjectTemplateResponseMixin, BaseCreateWithInlinesView):
    template_name_suffix = '_form'


class BaseUpdateWithInlinesView(ModelFormWithInlinesMixin, ProcessFormWithInlinesView):
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(BaseUpdateWithInlinesView, self).get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(BaseUpdateWithInlinesView, self).post(request, *args, **kwargs)


class UpdateWithInlinesView(SingleObjectTemplateResponseMixin, BaseUpdateWithInlinesView):
    template_name_suffix = '_form'
