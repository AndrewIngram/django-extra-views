django-extra-views - The missing class-based generic views for Django
=====================================================================

Django's class-based generic views are great, they let you accomplish a large number of web application design patterns in relatively few lines of code.  They do have their limits though, and that's what this library of views aims to overcome.

Features so far
------------------

- FormSet and ModelFormSet views - The formset equivalents of FormView and ModelFormView.
- InlineFormSetView - Lets you edit formsets related to a model (uses inlineformset_factory)
- CreateWithInlinesView and UpdateWithInlinesView - Lets you edit a model and its relations

Coming soon
-----------
- GenericInlineFormSetView
- Support for generic inlines in CreateWithInlinesView and UpdateWithInlinesView

Examples
--------

Defining a FormsetView. ::

    from extra_views import FormsetView
    
    class AddressFormset(FormsetView):
        form_class = AddressForm
        template_name = 'address_formset.html'

Defining a ModelFormsetView. ::

    from extra_views import ModelFormsetView:

    class ItemFormsetView(ModelFormsetView):
        model = Item
        template_name = 'item_formset.html'

Defining a CreateWithInlinesView. ::

    from extra_views import CreateWithInlinesView, InlineFormSet
    from extra_views.generic import GenericInlineFormSet

    class ItemInline(InlineFormSet):
        model = Item

    class TagInline(GenericInlineFormSet):
        model = Tag

    class CreateOrderView(CreateWithInlinesView):
        model = Order
        inlines = [ItemInline, TagInline]

More descriptive examples to come, take a look at the tests, they make good examples.
