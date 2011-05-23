from django.contrib.formtools.utils import form_hmac
from django.core.exceptions import ImproperlyConfigured
from django.utils.crypto import constant_time_compare

class FormPreviewMixin(object):
    u"""Reimplementation of Django's FormPreview as a Mixin for use with ProcessFormView"""
    preview_template = None
    stages = {'1': 'preview', '2': 'post'}
    auto_id = 'formtools_%s'
    
    def _check_security_hash(self, token, form):
        expected = self.security_hash(form)
        return constant_time_compare(token, expected)    
    
    def unused_name(self, form_class, name):
        while 1:
            try:
                form_class.base_fields[name]
            except KeyError:
                break  # This field name isn't being used by the form
            name += '_'
        return name
    
    def get_auto_id(self):
        return self.auto_id
    
    def get_form(self, form_class):
        return form_class(auto_id=self.get_auto_id(), **self.get_form_kwargs())
    
    def get_stage(self):
        return self.stages.get(self.request.POST.get(self.unused_name(self.get_form_class(), 'stage')), 'preview')

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        
        if self.get_stage() == 'confirm':
            if form.is_valid:
                if not self._check_security_hash(self.request.POST.get(self.unused_name('hash'), ''), form):
                    return self.failed_hash(form)
                return self.done(form.cleaned_data)
            else:
                return self.form_invalid(form)
        else:
            if form.is_valid():
                return self.preview(form)
            else:
                return self.form_invalid(form)

    def get_preview_templates(self):
        if self.preview_template is None:
            raise ImproperlyConfigured(
                "FormPreviewMixin requires either a definition of "
                "'preview_template or an implementation of 'get_preview_templates()'")
        else:
            return [self.preview_template]
        
    def render_preview_response(self, context, **response_kwargs):
        return self.response_class(
            request = self.request,
            template = self.get_preview_templates(),
            context = context,
            **response_kwargs
        )

    def get_context_data(self, *args, **kwargs):
        context = super(FormPreviewMixin, self).get_context_data(*args, **kwargs)
        context.update({
            'stage_field': self.unused_name(self.get_form_class(), 'stage'),
            'stage_value': self.get_stage(),
        })
        return context

    def preview(self, form):
        return self.render_preview_response(self.get_context_data(form=form,data=form.cleaned_data,hash_field=self.unused_name(self.get_form_class(), 'hash'),hash_value=self.security_hash(form)))
        
    def security_hash(self, form):
        return form_hmac(form)
    
    def failed_hash(self, form):
        return self.preview(form)
    
    def done(self, cleaned_data):
        raise NotImplementedError('You must define a done() method')
