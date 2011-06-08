django-extra-views - The missing class-based generic views for Django
=====================================================================

Django's class-based generic views are great, they let you accomplish a large number of web application design patterns in relatively few lines of code.  They do have their limits though, and that's what this library of views aims to overcome.

Features so far...
------------------

- Formset and ModelFormset views - The formset equivalents of FormView and ModelFormView.
- MultiFormView - Lets you handle multiple forms with differing post-validation logic within the same view.

In development
--------------

- Support for inline_formsets, either as part of ModelFormsetView or as a subclass.
- Support for Formsets and ModelFormsets in MultiFormView.

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
           'order': MultiFormView.modelform(Order),
           'address': MultiFormView.form(AddressForm),
       }
       template_name = 'orderandaddress_forms.html'
        
       def get_order_instance():
           return Order.objects.get(id=1)

More descriptive examples to come, take a look at the tests, they make good examples.
