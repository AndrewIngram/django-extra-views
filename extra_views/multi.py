from django.views.generic.base import TemplateResponseMixin, View
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django import forms


class MultiFormMixin(object):
    """
    Handle multiple forms in a single view
    """
    forms = {}
    initial = {}
    success_url = None
    identifier_field = 'form_id'
    
    def unused_name(self, form_class, name):
        while 1:
            try:
                form_class.base_fields[name]
            except KeyError:
                break  # This field name isn't being used by the form
            name += '_'
        return name    
    
    def get_initial(self,form_prefix):
        handler = 'get_initial_%s' % form_prefix
        if hasattr(self, handler):
            return getattr(self, handler)()
        return self.initial.get(form_prefix,{})
    
    def get_form_classes(self):
        return self.forms
    
    def get_form(self, prefix, form_class):
        form = form_class(prefix=prefix, **self.get_form_kwargs(prefix))
        control_field = self.unused_name(form_class, self.identifier_field)
        form.fields[control_field] = forms.CharField(widget=forms.HiddenInput(),required=True)
        return form
    
    def construct_forms(self):
        form_classes = self.get_form_classes()
        forms = {}
        
        for prefix, form_class in form_classes.iteritems():
            forms['%s_form' % prefix] = self.get_form(prefix, form_class)
        return forms        
    
    def get_form_kwargs(self,form_prefix):
        kwargs = {'initial': self.get_initial(form_prefix)}
        if self.request.method in ('POST', 'PUT'):
            form_class = self.forms[form_prefix]
            control_field = self.unused_name(form_class, self.identifier_field)
            if '%s-%s' % (form_prefix, control_field) in self.request.POST:
                kwargs.update({
                    'data': self.request.POST,
                    'files': self.request.FILES,
                })
        return kwargs

    def get_context_data(self, **kwargs):
        return kwargs
            
    def get_success_url(self):
        if self.success_url:
            url = self.success_url
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to. Provide a success_url.")
        return url
            
    def handle_valid(self, forms, valid_forms):
        pass
    
    def handle_invalid(self, forms, invalid_forms):
        pass          
            
    def forms_valid(self, forms, valid_forms):
        for form in valid_forms:
            handler = 'handle_valid_%s' % form.prefix
            if hasattr(self, handler):
                getattr(self, handler)(form, valid_forms)
        self.handle_valid(forms, valid_forms)
        return HttpResponseRedirect(self.get_success_url())
    
    def forms_invalid(self, forms, invalid_forms):
        for form in invalid_forms:
            handler = 'handle_invalid_%s' % form.prefix
            if hasattr(self, handler):
                getattr(self, handler)(form, invalid_forms)
        self.handle_invalid(forms, invalid_forms)
        return self.render_to_response(self.get_context_data(**forms))
    

class ProcessMultiFormView(View):
    """
    The equivalent of Django's ProcessFormView but for MultiForms
    """
    def get(self, request, *args, **kwargs):
        forms = self.construct_forms()
        return self.render_to_response(self.get_context_data(**forms))
    
    def post(self, request, *args, **kwargs):
        forms = self.construct_forms()
        valid = True
        valid_forms = []
        invalid_forms = []
        
        for form in forms.values():
            control_field = self.unused_name(form.__class__, self.identifier_field)
            # Only validate the form if it was POSTED, otherwise we don't care.
            if ('%s-%s' % (form.prefix, control_field) in self.request.POST):
                if form.is_valid():
                    del form.cleaned_data[control_field]
                    valid_forms.append(form)
                else:
                    invalid_forms.append(form)
                    valid = False
        if valid:
            return self.forms_valid(forms, valid_forms)
        else:
            return self.forms_invalid(forms, invalid_forms)
    
    def put(self, request, *args, **kwargs):
        return self.post(*args, **kwargs)


class BaseMultiFormView(MultiFormMixin, ProcessMultiFormView):
    pass


class MultiFormView(TemplateResponseMixin, BaseMultiFormView):
    pass
