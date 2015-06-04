django-extra-views - The missing class-based generic views for Django
========================================================================

Django's class-based generic views are great, they let you accomplish a large number of web application design patterns in relatively few lines of code.  They do have their limits though, and that's what this library of views aims to overcome.

.. image:: https://secure.travis-ci.org/AndrewIngram/django-extra-views.svg?branch=master
        :target: https://travis-ci.org/AndrewIngram/django-extra-views


Installation
------------

Installing from pypi (using pip). ::

    pip install django-extra-views

Installing from github. ::

    pip install -e git://github.com/AndrewIngram/django-extra-views.git#egg=django-extra-views


See the `documentation here`_

.. _documentation here: https://django-extra-views.readthedocs.org/en/latest/

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

Examples
--------

Defining a FormSetView. ::

    from extra_views import FormSetView


    class AddressFormSet(FormSetView):
        form_class = AddressForm
        template_name = 'address_formset.html'

Defining a ModelFormSetView. ::

    from extra_views import ModelFormSetView


    class ItemFormSetView(ModelFormSetView):
        model = Item
        template_name = 'item_formset.html'

Defining a CreateWithInlinesView and an UpdateWithInlinesView. ::

    from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet
    from extra_views.generic import GenericInlineFormSet


    class ItemInline(InlineFormSet):
        model = Item


    class TagInline(GenericInlineFormSet):
        model = Tag


    class CreateOrderView(CreateWithInlinesView):
        model = Order
        inlines = [ItemInline, TagInline]


    class UpdateOrderView(UpdateWithInlinesView):
        model = Order
        inlines = [ItemInline, TagInline]


    # Example URLs.
    urlpatterns = patterns('',
        url(r'^orders/new/$', CreateOrderView.as_view()),
        url(r'^orders/(?P<pk>\d+)/$', UpdateOrderView.as_view()),
    )
    
Other bits of functionality
---------------------------

If you want more control over the names of your formsets (as opposed to iterating over inlines), you can use NamedFormsetsMixin. ::

    from extra_views import NamedFormsetsMixin

    class CreateOrderView(NamedFormsetsMixin, CreateWithInlinesView):
        model = Order
        inlines = [ItemInline, TagInline]
        inlines_names = ['Items', 'Tags']

You can add search functionality to your ListViews by adding SearchableMixin and by setting search_fields::

    from django.views.generic import ListView
    from extra_views import SearchableListMixin

    class SearchableItemListView(SearchableListMixin, ListView):
        template_name = 'extra_views/item_list.html'
        search_fields = ['name', 'sku']
        model = Item

In this case ``object_list`` will be filtered if the 'q' query string is provided (like /searchable/?q=query), or you
can manually override ``get_search_query`` method, to define your own search functionality.

Also you can define some items  in ``search_fields`` as tuple (e.g. ``[('name', 'iexact', ), 'sku']``)
to provide custom lookups for searching. Default lookup is ``icontains``. We strongly recommend to use only
string lookups, when number fields will convert to strings before comparison to prevent converting errors.
This controlled by ``check_lookups`` setting of SearchableMixin.

Define sorting in view. ::

    from django.views.generic import ListView
    from extra_views import SortableListMixin

    class SortableItemListView(SortableListMixin, ListView):
        sort_fields_aliases = [('name', 'by_name'), ('id', 'by_id'), ]
        model = Item

You can hide real field names in query string by define sort_fields_aliases attribute (see example)
or show they as is by define sort_fields. SortableListMixin adds ``sort_helper`` variable of SortHelper class,
then in template you can use helper functions: ``{{ sort_helper.get_sort_query_by_FOO }}``,
``{{ sort_helper.get_sort_query_by_FOO_asc }}``, ``{{ sort_helper.get_sort_query_by_FOO_desc }}`` and
``{{ sort_helper.is_sorted_by_FOO }}``

More descriptive examples to come.
