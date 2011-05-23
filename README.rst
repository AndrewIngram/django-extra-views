django-extra-views - The missing class-based generic views for Django
=====================================================================

Django's class-based generic views are great, they let you accomplish a large number of web application design patterns in relatively few lines of code.  They do have their limits though, and that's what this library of views aims to overcome.

Features so far...
------------------

- Formset and ModelFormset views - The formset equivalents of FormView and ModelFormView
- MultiFormView - Lets you handle multiple forms with different handling logic within the same view.

In development
--------------

- FormPreviewMixin - A reimplentation of Django's FormPreview as a mixin for generic views. The aim is for it to be compatible with CreateView and UpdateView at the very least.
- Support for Formsets and ModelFormsets in MultiFormView

Planning Stages
---------------

- FormWizardView - The goal is a more powerful version of Django's existing FormWizard, if you have any particular grievances with the current one, let me know about it.


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

Defining a MultiFormView. ::

    from extra_views import MultiFormView

    class OrderAndAddressView(MultiFormView):
       forms = {
           'order': OrderForm,
           'address': AddressForm,
       }
       template_name = 'orderandaddress_forms.html'

More descriptive examples to come, take a look at the tests, they make good examples.
