from django.views.generic.base import TemplateResponseMixin, View
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect, Http404
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.forms import models as model_forms
from django.forms import ValidationError

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
        
        try:
            form = self.form_class(prefix=prefix, **kwargs)
        except ValidationError, e:
            # This is nasty.  Basically a formset will throw a validation error on instantiation
            # if the management form is missing, but we expect it to be empty if it wasn't one
            # of the POSTed forms, so we have to catch the error and deal with it later.
            form = e
            form.prefix = prefix
        return form


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
            return { 'all': self.forms }
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
            
    def forms_valid(self):
        return HttpResponseRedirect(self.get_success_url())
    
    def forms_invalid(self, forms):
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
        forms_dict = dict([(x.prefix, x) for x in forms.values()])
        
        valid = True
        valid_forms = {}
        invalid_forms = {}
        
        posted_prefixes = []
        
        # First we detect which prefixes were POSTed
        for prefix in self.get_form_definitions().keys():
            for field in self.request.POST:
                if field.startswith(prefix):
                    posted_prefixes.append(prefix)
                    break

        # Now we iterated over the groups until we find one that matches the POSTed prefixes
        for label, prefixes in self.get_groups().iteritems():
            if label == 'all' or list(prefixes) == posted_prefixes:
                # We've found the group, now check if all its forms are valid
                for prefix in prefixes:
                    form = forms_dict[prefix]

                    # FormSets force us to do this...
                    if isinstance(form, ValidationError):
                        raise form
                    
                    if form.is_valid():
                        valid_forms[prefix] = form
                    else:
                        valid = False
                        invalid_forms[prefix] = form
                if valid:
                    handler = 'valid_%s' % label
                    if hasattr(self, handler):
                        getattr(self, handler)(valid_forms)
                    return self.forms_valid()
                else:
                    handler = 'invalid_%s' % label
                    if hasattr(self, handler):
                        getattr(self, handler)(invalid_forms)                    
                    return self.forms_invalid(forms)
                break
            
        # If we got here, it means we couldn't find a matching group for the POST data
        raise Http404()
    
    def put(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class BaseMultiFormView(MultiFormMixin, ProcessMultiFormView):
    pass


class MultiFormView(TemplateResponseMixin, BaseMultiFormView):
    pass
