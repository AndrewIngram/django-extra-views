|travis| |codecov|

django-extra-views - The missing class-based generic views for Django
========================================================================

Django's class-based generic views are great, they let you accomplish a large number of web application design patterns in relatively few lines of code.  They do have their limits though, and that's what this library of views aims to overcome.

.. |travis| image:: https://secure.travis-ci.org/AndrewIngram/django-extra-views.svg?branch=master
        :target: https://travis-ci.org/AndrewIngram/django-extra-views

.. |codecov| image:: https://codecov.io/github/AndrewIngram/django-extra-views/coverage.svg?branch=master
    :target: https://codecov.io/github/AndrewIngram/django-extra-views?branch=master


Installation
------------

Installing from pypi (using pip). ::

    pip install django-extra-views

Installing from github. ::

    pip install -e git://github.com/AndrewIngram/django-extra-views.git#egg=django-extra-views


See the `full documentation here`_

.. _full documentation here: https://django-extra-views.readthedocs.org/en/latest/

Features so far
------------------

- FormSet and ModelFormSet views - The formset equivalents of FormView and ModelFormView.
- InlineFormSetView - Lets you edit formsets related to a model (uses inlineformset_factory)
- CreateWithInlinesView and UpdateWithInlinesView - Lets you edit a model and its relations
- GenericInlineFormSetView, the equivalent of InlineFormSetView but for GenericForeignKeys
- Support for generic inlines in CreateWithInlinesView and UpdateWithInlinesView
- Support for naming each inline or formset with NamedFormsetsMixin
- SortableListMixin - Generic mixin for sorting functionality in your views
- SearchableListMixin - Generic mixin for search functionality in your views

Still to do
-----------

I'd like to add support for pagination in ModelFormSetView and its derivatives, the goal being to be able to mimic the change_list view in Django's admin. Currently this is proving difficult because of how Django's MultipleObjectMixin handles pagination.

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


