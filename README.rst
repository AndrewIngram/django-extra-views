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

.. include:: docs/pages/installation.rst

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

.. include:: docs/pages/quick-examples.rst