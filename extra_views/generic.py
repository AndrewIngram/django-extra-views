from django.contrib.contenttypes.generic import generic_inlineformset_factory, BaseGenericInlineFormSet
from extra_views.formsets import BaseInlineFormSetMixin, InlineFormSetMixin, BaseInlineFormSetView, InlineFormSetView

class BaseGenericInlineFormSetMixin(BaseInlineFormSetMixin):
    ct_field = "content_type"
    ct_fk_field = "object_id"
    formset_class = BaseGenericInlineFormSet
    
    def get_factory_kwargs(self):
        kwargs = super(BaseGenericInlineFormSetMixin, self).get_factory_kwargs()
        del kwargs['fk_name']
        kwargs.update({
            "ct_field": self.ct_field,
            "fk_field": self.ct_fk_field,
        })
        return kwargs
    
    def get_formset(self):
        result = generic_inlineformset_factory(self.inline_model, **self.get_factory_kwargs())
        return result


class GenericInlineFormSet(BaseGenericInlineFormSetMixin):
    def __init__(self, parent_model, request, instance):
        self.inline_model = self.model
        self.model = parent_model
        self.request = request
        self.object = instance
    

class GenericInlineFormSetMixin(BaseGenericInlineFormSetMixin, InlineFormSetMixin):
    pass


class BaseGenericInlineFormSetView(GenericInlineFormSetMixin, BaseInlineFormSetView):
    pass


class GenericInlineFormSetView(BaseGenericInlineFormSetView, InlineFormSetView):
    pass