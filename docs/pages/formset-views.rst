Formset Views
=============

For all of these views we've tried to mimic the API of Django's existing class-based
views as closely as possible, so they should feel natural to anyone who's already
familiar with Django's views.


FormSetView
-----------

This is the formset equivalent of Django's FormView. Use it when you want to
display a single (non-model) formset on a page.

A simple formset:

.. code-block:: python

    from extra_views import FormSetView
    from my_app.forms import AddressForm
    

    class AddressFormSetView(FormSetView):
        template_name = 'address_formset.html'
        form_class = AddressForm
        success_url = 'success/'

        def get_initial(self):
            # return whatever you'd normally use as the initial data for your formset.
          return data

        def formset_valid(self, formset):
            # do whatever you'd like to do with the valid formset
            return super(AddressFormSetView, self).formset_valid(formset)

and in ``address_formset.html``:

.. code-block:: html

    <form method="post">
      ...
      {{ formset }}
      ...
      <input type="submit" value="Submit" />
    </form>

This view will render the template ``address_formset.html`` with a context variable
:code:`formset` representing the :code:`AddressFormSet`. Once POSTed and successfully
validated, :code:`formset_valid` will be called (which is where your handling logic
goes), then the view will redirect to :code:`success_url`.

Formset constructor and factory kwargs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

FormSetView exposes all the parameters you'd normally be able to pass to the
:code:`django.forms.BaseFormSet` constructor and
:code:`django.forms.formset_factory()`. This can be done by setting the
respective attribute on the class, or :code:`formset_kwargs` and
:code:`factory_kwargs` at the class level.

Below is an exhaustive list of all formset-related attributes which can be set
at the class level for :code:`FormSetView`:

.. code-block:: python

    ...
    from my_app.forms import AddressForm, BaseAddressFormSet


    class AddressFormSetView(FormSetView):
        template_name = 'address_formset.html'
        form_class = AddressForm
        formset_class = BaseAddressFormSet
        initial = [{'type': 'home'}, {'type': 'work'}]
        prefix = 'address-form'
        success_url = 'success/'
        factory_kwargs = {'extra': 2, 'max_num': None,
                          'can_order': False, 'can_delete': False}
        formset_kwargs = {'auto_id': 'my_id_%s'}

In the above example, BaseAddressFormSet would be a subclass of
:code:`django.forms.BaseFormSet`.

ModelFormSetView
----------------

ModelFormSetView makes use of :code:`django.forms.modelformset_factory()`, using the
declarative syntax used in :code:`FormSetView` as well as Django's own class-based
views. So as you'd expect, the simplest usage is as follows:

.. code-block:: python

    from extra_views import ModelFormSetView
    from my_app.models import Item


    class ItemFormSetView(ModelFormSetView):
        model = Item
        fields = ['name', 'sku', 'price']
        template_name = 'item_formset.html'

Rather than setting :code:`fields`, :code:`exclude` can be defined
at the class level as a list of fields to be excluded.

It is not necessary to define :code:`fields` or :code:`exclude` if a
:code:`form_class` is defined at the class level:

.. code-block:: python

    ...
    from django.forms import ModelForm


    class ItemForm(ModelForm):
        # Custom form definition goes here
        fields = ['name', 'sku', 'price']


    class ItemFormSetView(ModelFormSetView):
        model = Item
        form_class = ItemForm
        template_name = 'item_formset.html'

Like :code:`FormSetView`, the :code:`formset` variable is made available in the template
context. By default this will populate the formset with all the instances of
:code:`Item` in the database. You can control this by overriding :code:`get_queryset` on
the class, which could filter on a URL kwarg (:code:`self.kwargs`), for example:

.. code-block:: python

    class ItemFormSetView(ModelFormSetView):
        model = Item
        template_name = 'item_formset.html'

        def get_queryset(self):
            sku = self.kwargs['sku']
            return super(ItemFormSetView, self).get_queryset().filter(sku=sku)


InlineFormSetView
-----------------

When you want to edit instances of a particular model related to a parent model
(using a ForeignKey), you'll want to use InlineFormSetView. An example use case
would be editing addresses associated with a particular contact.

.. code-block:: python

    from extra_views import InlineFormSetView


    class EditContactAddresses(InlineFormSetView):
        model = Contact
        inline_model = Address

        ...

Aside from the use of :code:`model` and :code:`inline_model`,
:code:`InlineFormSetView` works more-or-less in the same way as
:code:`ModelFormSetView`, instead calling :code:`django.forms.inlineformset_factory()`.

CreateWithInlinesView and UpdateWithInlinesView
-----------------------------------------------

These are the most powerful views in the library, they are effectively
replacements for Django's own :code:`CreateView` and :code:`UpdateView`. The key
difference is that they let you include any number of inline formsets (as well
as the parent model's form). This provides functionality much like the Django
Admin change forms. The API should be fairly familiar as well. The list of the
inlines will be passed to the template as context variable `inlines`.

Here is a simple example that demonstrates the use of each view with normal
inline relationships:

.. code-block:: python

    from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSetFactory


    class ItemInline(InlineFormSetFactory):
        model = Item
        fields = ['sku', 'price', 'name']


    class ContactInline(InlineFormSetFactory):
        model = Contact
        fields = ['name', 'email']


    class CreateOrderView(CreateWithInlinesView):
        model = Order
        inlines = [ItemInline, ContactInline]
        fields = ['customer', 'name']
        template_name = 'order_and_items.html'

        def get_success_url(self):
            return self.object.get_absolute_url()


    class UpdateOrderView(UpdateWithInlinesView):
        model = Order
        inlines = [ItemInline, ContactInline]
        fields = ['customer', 'name']
        template_name = 'order_and_items.html'

        def get_success_url(self):
            return self.object.get_absolute_url()

and in the html template:

.. code-block:: html

    <form method="post">
      ...
      {{ form }}

      {% for formset in inlines %}
        {{ formset }}
      {% endfor %}
      ...
      <input type="submit" value="Submit" />
    </form>

InlineFormSetFactory
^^^^^^^^^^^^^^^^^^^^
This class represents all the configuration necessary to generate an inline formset
from :code:`django.inlineformset_factory()`. Each class within in
:code:`CreateWithInlines.inlines` and :code:`UpdateWithInlines.inlines`
should be a subclass of :code:`InlineFormSetFactory`. All the
same methods and attributes as :code:`InlineFormSetView` are available, with the
exception of any view-related attributes and methods, such as :code:`success_url`
or :code:`formset_valid()`:

.. code-block:: python

    from my_app.forms import ItemForm, BaseItemFormSet
    from extra_views import InlineFormSetFactory


    class ItemInline(InlineFormSetFactory):
        model = Item
        form_class = ItemForm
        formset_class = BaseItemFormSet
        initial = [{'name': 'example1'}, {'name', 'example2'}]
        prefix = 'item-form'
        factory_kwargs = {'extra': 2, 'max_num': None,
                          'can_order': False, 'can_delete': False}
        formset_kwargs = {'auto_id': 'my_id_%s'}


**IMPORTANT**: Note that when using :code:`InlineFormSetFactory`, :code:`model` should be the
*inline* model and **not** the parent model.

GenericInlineFormSetView
------------------------

In the specific case when you would usually use Django's
:code:`django.contrib.contenttypes.forms.generic_inlineformset_factory()`, you
should use :code:`GenericInlineFormSetView`. The kwargs :code:`ct_field` and
:code:`fk_field` should be set in :code:`factory_kwargs` if they need to be
changed from their default values:

.. code-block:: python

    from extra_views.generic import GenericInlineFormSetView


    class EditOrderTags(GenericInlineFormSetView):
        model = Order
        inline_model = Tag
        factory_kwargs = {'ct_field': 'content_type', 'fk_field': 'object_id',
                          'max_num': 1}
        formset_kwargs = {'save_as_new': True}

        ...

There is a :code:`GenericInlineFormSetFactory` which is analogous to
:code:`InlineFormSetFactory` for use with generic inline formsets.

:code:`GenericInlineFormSetFactory` can be used in
:code:`CreateWithInlines.inlines` and :code:`UpdateWithInlines.inlines` in the
obvious way.
