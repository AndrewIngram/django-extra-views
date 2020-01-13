Formset Customization Examples
==============================

Overriding formset_kwargs and factory_kwargs at run time
-------------------------------------------------------------------------
If the values in :code:`formset_kwargs` and :code:`factory_kwargs` need to be
modified at run time, they can be set by overloading the :code:`get_formset_kwargs()`
and :code:`get_factory_kwargs()` methods on any formset view (model, inline or generic)
and the :code:`InlineFormSetFactory` classes:

.. code-block:: python

    class AddressFormSetView(FormSetView):
        ...

        def get_formset_kwargs(self):
            kwargs = super(AddressFormSetView, self).get_formset_kwargs()
            # modify kwargs here
            return kwargs

        def get_factory_kwargs(self):
            kwargs = super(AddressFormSetView, self).get_factory_kwargs()
            # modify kwargs here
            return kwargs


Overriding the the base formset class
-------------------------------------

The :code:`formset_class` option should be used if you intend to override the
formset methods of a view or a subclass of :code:`InlineFormSetFactory`.

For example, imagine you'd like to add your custom :code:`clean` method
for an inline formset view. Then, define a custom formset class, a subclass of
Django's :code:`BaseInlineFormSet`, like this:

.. code-block:: python

    from django.forms.models import BaseInlineFormSet

    class ItemInlineFormSet(BaseInlineFormSet):

        def clean(self):
            # ...
            # Your custom clean logic goes here


Now, in your :code:`InlineFormSetView` sub-class, use your formset class via
:code:`formset_class` setting, like this:

.. code-block:: python

    from extra_views import InlineFormSetView
    from my_app.models import Item
    from my_app.forms import ItemForm

    class ItemInlineView(InlineFormSetView):
        model = Item
        form_class = ItemForm
        formset_class = ItemInlineFormSet     # enables our custom inline

This will enable :code:`clean` method being executed on the formset used by
:code:`ItemInlineView`.

Initial data for ModelFormSet and InlineFormSet
-----------------------------------------------

Passing initial data into ModelFormSet and InlineFormSet works slightly
differently to a regular FormSet. The data passed in from :code:`initial` will
be inserted into the :code:`extra` forms of the formset. Only the data from
:code:`get_queryset()` will be inserted into the initial rows:

.. code-block:: python

    from extra_views import ModelFormSetView
    from my_app.models import Item


    class ItemFormSetView(ModelFormSetView):
        template_name = 'item_formset.html'
        model = Item
        factory_kwargs = {'extra': 10}
        initial = [{'name': 'example1'}, {'name': 'example2'}]

The above will result in a formset containing a form for each instance of
:code:`Item` in the database, followed by 2 forms containing the extra initial data,
followed by 8 empty forms.

Altenatively, initial data can be determined at run time and passed in by
overloading :code:`get_initial()`:

.. code-block:: python

    ...
    class ItemFormSetView(ModelFormSetView):
        model = Item
        template_name = 'item_formset.html'
        ...

        def get_initial(self):
            # Get a list of initial values for the formset here
            initial = [...]
            return initial

Passing arguments to the form constructor
-----------------------------------------

In order to change the arguments which are passed into each form within the
formset, this can be done by the 'form_kwargs' argument passed in to the FormSet
constructor. For example, to give every form an initial value of 'example'
in the 'name' field:

.. code-block:: python

    from extra_views import InlineFormSetFactory

    class ItemInline(InlineFormSetFactory):
        model = Item
        formset_kwargs = {'form_kwargs': {'initial': {'name': 'example'}}}

If these need to be modified at run time, it can be done by
:code:`get_formset_kwargs()`:

.. code-block:: python

    from extra_views import InlineFormSetFactory

    class ItemInline(InlineFormSetFactory):
        model = Item

        def get_formset_kwargs(self):
            kwargs = super(ItemInline, self).get_formset_kwargs()
            initial = get_some_initial_values()
            kwargs['form_kwargs'].update({'initial': initial})
            return kwargs


Named formsets
--------------
If you want more control over the names of your formsets (as opposed to
iterating over :code:`inlines`), you can use :code:`NamedFormsetsMixin`:

.. code-block:: python

    from extra_views import NamedFormsetsMixin

    class CreateOrderView(NamedFormsetsMixin, CreateWithInlinesView):
        model = Order
        inlines = [ItemInline, TagInline]
        inlines_names = ['Items', 'Tags']
        fields = '__all__'

Then use the appropriate names to render them in the html template:

.. code-block:: html

    ...
    {{ Tags }}
    ...
    {{ Items }}
    ...

Success messages
----------------
When using Django's messages framework, mixins are available to send success
messages in a similar way to ``django.contrib.messages.views.SuccessMessageMixin``.
Ensure that :code:`'django.contrib.messages.middleware.MessageMiddleware'` is included
in the ``MIDDLEWARE`` section of `settings.py`.

:code:`extra_views.SuccessMessageMixin` is for use with views with multiple
inline formsets. It is used in an identical manner to Django's
SuccessMessageMixin_, making :code:`form.cleaned_data` available for string
interpolation using the :code:`%(field_name)s` syntax:

.. _SuccessMessageMixin: https://docs.djangoproject.com/en/dev/ref/contrib/messages/#django.contrib.messages.views.SuccessMessageMixin

.. code-block:: python

    from extra_views import CreateWithInlinesView, SuccessMessageMixin
    ...

    class CreateOrderView(SuccessMessageMixin, CreateWithInlinesView):
        model = Order
        inlines = [ItemInline, ContactInline]
        success_message = 'Order %(name)s successfully created!'
        ...

        # or instead, set at runtime:
        def get_success_message(self, cleaned_data, inlines):
            return 'Order with id {} successfully created'.format(self.object.pk)

Note that the success message mixins should be placed ahead of the main view in
order of class inheritance.

:code:`extra_views.FormSetSuccessMessageMixin` is for use with views which handle a single
formset. In order to parse any data from the formset, you should override the
:code:`get_success_message` method as below:

.. code-block:: python

    from extra_views import FormSetView, FormSetSuccessMessageMixin
    from my_app.forms import AddressForm


    class AddressFormSetView(FormSetView):
        form_class = AddressForm
        success_url = 'success/'
        ...
        success_message = 'Addresses Updated!'

    # or instead, set at runtime
    def get_success_message(self, formset)
        # Here you can use the formset in the message if required
        return '{} addresses were updated.'.format(len(formset.forms))
