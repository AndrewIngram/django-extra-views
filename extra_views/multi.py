from django.views.generic.base import TemplateResponseMixin, View
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.forms import models as model_forms


class FormProvider(object):   
    def __init__(self, form_class, context_suffix, init_args={}):
        self.form_class = form_class
        self.context_suffix = context_suffix
        self.init_args = init_args
        
    def get_context_suffix(self):
        return self.context_suffix
    
    def get_form(self, caller, prefix):
        kwargs = {}
        
        for k,v in self.init_args.iteritems():
            method_name = v % prefix
            try:
                kwargs[k] = getattr(caller, method_name)()
            except AttributeError:
                
                msg = '%s must implement method "%s" ' % (caller.__class__.__name__, method_name)
                raise ImproperlyConfigured(msg)
        kwargs.update(caller.get_form_kwargs(prefix))
        
        return self.form_class(prefix=prefix, **kwargs)


class MultiFormMixin(object):
    """
    Handle multiple forms in a single view
    """
    forms = {}
    initial = {}
    success_url = None
    groups = None
    
    @staticmethod
    def form(form):
        return FormProvider(form_class=form, context_suffix='form')
    
    @staticmethod
    def modelform(model, form=None, **kwargs):
        if not form:
            form = model_forms.modelform_factory(model, **kwargs)
        return FormProvider(form_class=form, context_suffix='form' , init_args={'instance': 'get_%s_instance'})

    @staticmethod
    def formset(form, **kwargs):
        generated_formset = formset_factory(form, **kwargs)
        return FormProvider(form_class=generated_formset, context_suffix='formset')
    
    @staticmethod
    def modelformset(model, **kwargs):
        generated_formset = modelformset_factory(model, **kwargs)
        return FormProvider(form_class=generated_formset, context_suffix='formset', init_args={'queryset': 'get_%s_queryset'})
    
    def get_initial(self,prefix):
        handler = 'get_initial_%s' % prefix
        if hasattr(self, handler):
            return getattr(self, handler)()
        return self.initial.get(prefix,{})
    
    def get_form_definitions(self):
        return self.forms
    
    def get_groups(self):
        if not self.groups:
            return dict([(k, k) for k in self.forms])
        return self.groups

    def construct_forms(self):
        forms = {}
        definitions = self.get_form_definitions()
        
        for prefix, provider in definitions.iteritems():
            context_name = '%s_%s' % (prefix, provider.get_context_suffix())
            forms[context_name] = provider.get_form(self, prefix)
        return forms        
    
    def get_form_kwargs(self,prefix):
        kwargs = {'initial': self.get_initial(prefix)}
        if self.request.method in ('POST', 'PUT'):
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
            handler = 'valid_%s' % form.prefix
            if hasattr(self, handler):
                getattr(self, handler)(form, valid_forms)
        self.handle_valid(forms, valid_forms)
        return HttpResponseRedirect(self.get_success_url())
    
    def forms_invalid(self, forms, invalid_forms):
        for form in invalid_forms:
            handler = 'invalid_%s' % form.prefix
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
            if form.is_valid():
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
