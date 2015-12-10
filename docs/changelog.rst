Change History
==============

1.0.0 (TBA)
-----------
This version supports Django 1.6, 1.7, 1.8, 1.9 (latest minor versions), and Python 2.7, 3.4, 3.5 (latest minor versions).

Backwards-incompatible changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Dropped support for Django < 1.6, and Python 3.3.
- Removed the ``extra_views.multi`` module as it had neither documentation nor
  test coverage and was broken for some of the supported Django/Python
  versions.
- Fixed #114: Don't implicitly set ``fields = '__all__'``.  If you face
  ``ImproperlyConfigured`` exceptions, you should have a look at the
  `Django 1.6 release notes`_ and set the ``fields`` or ``exclude`` attributes
  on your ``ModelForm`` or extra-views views.

.. _Django 1.6 release notes: https://docs.djangoproject.com/en/stable/releases/1.6/#modelform-without-fields-or-exclude


0.7.1 (2015-06-15)
------------------
Begin of this changelog.
