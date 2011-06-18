from django.contrib.contenttypes.generic import generic_inlineformset_factory, BaseGenericInlineFormSet
from extra_views.formsets import BaseInlineFormSetMixin, InlineFormSetMixin, BaseInlineFormSetView, InlineFormSetView
from extra_views.advanced import InlineFormSet

class BaseGenericInlineFormSetMixin(BaseInlineFormSetMixin):
    ct_field = "content_type"
    ct_fk_field = "object_id"
    formset = BaseGenericInlineFormSet
    
    def get_factory_kwargs(self):
        kwargs = super(BaseGenericInlineFormSetMixin, self).get_factory_kwargs()
        del kwargs['fk_name']
        kwargs.update({
            "ct_field": self.ct_field,
            "fk_field": self.ct_fk_field,
        })
        return kwargs
    
    def get_formset(self):
        return generic_inlineformset_factory(self.model, **self.get_factory_kwargs())


class GenericInlineFormSet(BaseGenericInlineFormSetMixin):
    def __init__(self, parent_model, request, instance):
        self.request = request
        self.object = instance
    

class GenericInlineFormSetMixin(BaseGenericInlineFormSetMixin, InlineFormSetMixin):
    pass


class BaseGenericInlineFormSetView(GenericInlineFormSetMixin, BaseInlineFormSetView):
    pass


class GenericInlineFormSetView(BaseGenericInlineFormSetView, InlineFormSetView):
    pass