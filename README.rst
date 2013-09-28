django-extra-views - Refactored to Vanilla style
================================================

Django's class-based generic views are great, they let you accomplish a large number of web application design patterns in relatively few lines of code.  They do have their limits though, and that's what this library of views aims to overcome.

.. image:: https://api.travis-ci.org/AndrewIngram/django-extra-views.png?branch=master
        :target: https://travis-ci.org/AndrewIngram/django-extra-views

.. image:: https://pypip.in/d/django-extra-views/badge.png
        :target: https://crate.io/packages/django-extra-views/

Installation
------------

Installing from github. ::

    pip install -e git://github.com/tomchristie/django-extra-views.git#egg=django-extra-views

.. _`Documentation`: https://django-extra-views.readthedocs.org/en/latest/

Features so far
------------------

- FormSet and ModelFormSet views - The formset equivalents of FormView and ModelFormView.
- InlineFormSetView - Lets you edit formsets related to a model (uses inlineformset_factory)
- GenericInlineFormSetView, the equivalent of InlineFormSetView but for GenericForeignKeys
- CreateWithInlinesView and UpdateWithInlinesView - Lets you edit a model and its relations
- Support for generic inlines in CreateWithInlinesView and UpdateWithInlinesView

Notes
-----

- NamedFormsetMixin removed - context behavior baked directly into views, with ``inline_context_names`` and ``formset_context_name``.
- Removed ``MultiFormView``, ``SearchableMixin``, ``SortableListMixin``, ``CalendarMonthView``.

Still to do
-----------

Adding support for pagination in ModelFormSetView and its derivatives should now be simpler.

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
