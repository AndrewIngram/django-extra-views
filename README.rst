|travis| |codecov| |docs-status|

Django Extra Views - The missing class-based generic views for Django
========================================================================

Django-extra-views is a Django package which introduces additional class-based views
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

.. include:: docs/pages/features.rst

Still to do
-----------

Add support for pagination in ModelFormSetView and its derivatives, the goal
being to be able to mimic the change_list view in Django's admin. Currently this
is proving difficult because of how Django's MultipleObjectMixin handles pagination.

.. include:: docs/pages/quick-examples.rst
