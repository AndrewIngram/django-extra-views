from django.views.generic.base import TemplateResponseMixin, View

class MultiViewMixin(object):
    """
    Handle multiple forms and formsets in a single view
    """
    forms = {}
    initial = {}
    
    def get_initial(self,form_prefix):
        return self.initial.get(form_prefix,None)

    def get_form_classes(self):
        return self.forms

    def get_context_data(self, forms):
        return {}


class MultiViewProcess(View):
    def get(self, request, *args, **kwargs):
        form_classes = self.get_form_classes()
        forms = []
        
        for prefix, cls in form_classes.iteritems():
            forms.append(cls(self.get_initial(prefix)))
        return self.render_to_response(self.get_context_data(forms))


class BaseMultiView(MultiViewProcess, MultiViewMixin):
    pass


class MultiView(TemplateResponseMixin, BaseMultiView):
    pass
