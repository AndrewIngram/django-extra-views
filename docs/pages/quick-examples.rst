Quick Examples
--------------

FormSetView
^^^^^^^^^^^^^^^^^^^^^^^

Define a :code:`FormSetView`, a view which creates a single formset from
:code:`django.forms.formset_factory` and adds it to the context.

.. code-block:: python

    from extra_views import FormSetView
    from my_forms import AddressForm

    class AddressFormSet(FormSetView):
        form_class = AddressForm
        template_name = 'address_formset.html'

Then within ``address_formset.html``, render the formset like this:

.. code-block:: html

    <form method="post">
      ...
      {{ formset }}
      ...
      <input type="submit" value="Submit" />
    </form>

ModelFormSetView
^^^^^^^^^^^^^^^^^^^^

Define a :code:`ModelFormSetView`, a view which works as :code:`FormSetView`
but instead renders a model formset using
:code:`django.forms.modelformset_factory`.

.. code-block:: python

    from extra_views import ModelFormSetView


    class ItemFormSetView(ModelFormSetView):
        model = Item
        fields = ['name', 'sku']
        template_name = 'item_formset.html'

CreateWithInlinesView or UpdateWithInlinesView
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Define :code:`CreateWithInlinesView` and :code:`UpdateWithInlinesView`,
views which render a form to create/update a model instance and its related
inline formsets. Each of the :code:`InlineFormSetFactory` classes use similar
class definitions as the :code:`ModelFormSetView`.

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


    class UpdateOrderView(UpdateWithInlinesView):
        model = Order
        inlines = [ItemInline, ContactInline]
        fields = ['customer', 'name']
        template_name = 'order_and_items.html'


Then within ``order_and_items.html``, render the formset like this:

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