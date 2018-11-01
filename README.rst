|travis| |codecov| |docs-status|

Django Extra Views - The missing class-based generic views for Django
========================================================================

Django-extra-views is a Django app which introduces additional class-based views
in order to simplify common design patterns such as those found in the Django
admin interface.

Full documentation is available at `read the docs`_.

.. _read the docs: https://django-extra-views.readthedocs.io/

.. |travis| image:: https://secure.travis-ci.org/AndrewIngram/django-extra-views.svg?branch=master
    :target: https://travis-ci.org/AndrewIngram/django-extra-views
    :alt: Build Status

.. |codecov| image:: https://codecov.io/github/AndrewIngram/django-extra-views/coverage.svg?branch=master
    :target: https://codecov.io/github/AndrewIngram/django-extra-views?branch=master
    :alt: Coverage Status

.. |docs-status| image:: https://readthedocs.org/projects/django-extra-views/badge/?version=latest
    :target: https://django-extra-views.readthedocs.io/
    :alt: Documentation Status


Installation
------------

Install the stable release from pypi (using pip):

.. code-block:: sh

    pip install django-extra-views

Or install the current master branch from github:

.. code-block:: sh

    pip install -e git://github.com/AndrewIngram/django-extra-views.git#egg=django-extra-views

Then add ``'extra_views'`` to your ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'extra_views',
        ...
    ]

Features
--------

- ``FormSet`` and ``ModelFormSet`` views - The formset equivalents of
  ``FormView`` and ``ModelFormView``.
- ``InlineFormSetView`` - Lets you edit a formset related to a model (using
  Django's ``inlineformset_factory``).
- ``CreateWithInlinesView`` and ``UpdateWithInlinesView`` - Lets you edit a
  model and multiple inline formsets all in one view.
- ``GenericInlineFormSetView``, the equivalent of ``InlineFormSetView`` but for
  ``GenericForeignKeys``.
- Support for generic inlines in ``CreateWithInlinesView`` and
  ``UpdateWithInlinesView``.
- Support for naming each inline or formset in the template context with
  ``NamedFormsetsMixin``.
- ``SortableListMixin`` - Generic mixin for sorting functionality in your views.
- ``SearchableListMixin`` - Generic mixin for search functionality in your views.

Still to do
-----------

Add support for pagination in ModelFormSetView and its derivatives, the goal
being to be able to mimic the change_list view in Django's admin. Currently this
is proving difficult because of how Django's MultipleObjectMixin handles pagination.

Quick Examples
--------------

Defining a FormSetView.

.. code-block:: python

    from extra_views import FormSetView


    class AddressFormSet(FormSetView):
        form_class = AddressForm
        template_name = 'address_formset.html'

Defining a ModelFormSetView.

.. code-block:: python

    from extra_views import ModelFormSetView


    class ItemFormSetView(ModelFormSetView):
        model = Item
        template_name = 'item_formset.html'
        fields = '__all__'

Defining a CreateWithInlinesView and an UpdateWithInlinesView.

.. code-block:: python

    from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSetFactory
    from extra_views.generic import GenericInlineFormSetFactory


    class ItemInline(InlineFormSetFactory):
        model = Item
        fields = '__all__'


    class TagInline(GenericInlineFormSetFactory):
        model = Tag
        fields = '__all__'


    class CreateOrderView(CreateWithInlinesView):
        model = Order
        inlines = [ItemInline, TagInline]
        fields = '__all__'


    class UpdateOrderView(UpdateWithInlinesView):
        model = Order
        inlines = [ItemInline, TagInline]
        fields = '__all__'


    # Example URLs.
    urlpatterns = [
        url(r'^orders/new/$', CreateOrderView.as_view()),
        url(r'^orders/(?P<pk>\d+)/$', UpdateOrderView.as_view()),
        ]


