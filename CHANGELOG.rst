Change History
==============

0.14.0 (2021-06-08)
-------------------------

Changes:
~~~~~~~~
Supported Versions:

======== ==========
Python     Django
======== ==========
3.5      2.1–2.2
3.6-3.7  2.1–3.1
3.8      2.2–3.1
======== ==========

- Removed support for Python 2.7.
- Added support for Python 3.8 and Django 3.1.
- Removed the following classes (use the class in parentheses instead):

  - ``BaseFormSetMixin`` (use ``BaseFormSetFactory``).
  - ``BaseInlineFormSetMixin`` (use ``BaseInlineFormSetFactory``).
  - ``InlineFormSet`` (use ``InlineFormSetFactory``).
  - ``BaseGenericInlineFormSetMixin`` (use ``BaseGenericInlineFormSetFactory``).
  - ``GenericInlineFormSet`` (use ``GenericInlineFormSetFactory``).

0.13.0 (2019-12-20)
-------------------------

Changes:
~~~~~~~~
Supported Versions:

======== ==========
Python     Django
======== ==========
2.7      1.11
3.5      1.11–2.2
3.6-3.7  1.11–3.0
======== ==========

- Added ``SuccessMessageMixin`` and ``FormSetSuccessMessageMixin``.
- ``CreateWithInlinesView`` and ``UpdateWithInlinesView`` now call ``self.form_valid``
  method within ``self.forms_valid``.
- Revert ``view.object`` back to it's original value from the GET request if
  validation fails for the inline formsets in ``CreateWithInlinesView`` and
  ``UpdateWithInlinesview``.
- Added support for Django 3.0.

0.12.0 (2018-10-21)
-------------------
Supported Versions:

======== ==========
Python     Django
======== ==========
2.7      1.11
3.4      1.11–2.0
3.5-3.7  1.11–2.1
======== ==========

Changes:
~~~~~~~~
- Removed setting of ``BaseInlineFormSetMixin.formset_class`` and
  ``GenericInlineFormSetMixin.formset_class`` so that ``formset`` can be set in
  ``factory_kwargs`` instead.
- Removed ``ModelFormSetMixin.get_context_data`` and
  ``BaseInlineFormSetMixin.get_context_data`` as this code was duplicated from
  Django's ``MultipleObjectMixin`` and ``SingleObjectMixin`` respectively.
- Renamed ``BaseFormSetMixin`` to ``BaseFormSetFactory``.
- Renamed ``BaseInlineFormSetMixin`` to ``BaseInlineFormSetFactory``.
- Renamed ``InlineFormSet`` to ``InlineFormSetFactory``.
- Renamed ``BaseGenericInlineFormSetMixin`` to ``BaseGenericInlineFormSetFactory``.
- Renamed ``GenericInlineFormSet`` to ``GenericInlineFormSetFactory``.

All renamed classes will be removed in a future release.


0.11.0 (2018-04-24)
-------------------
Supported Versions:

======== ==========
Python     Django
======== ==========
2.7      1.11
3.4–3.6  1.11–2.0
======== ==========

Backwards-incompatible changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Dropped support for Django 1.7–1.10.
- Removed support for factory kwargs ``extra``, ``max_num``, ``can_order``,
  ``can_delete``, ``ct_field``, ``formfield_callback``, ``fk_name``,
  ``widgets``, ``ct_fk_field`` being set on ``BaseFormSetMixin`` and its
  subclasses. Use ``BaseFormSetMixin.factory_kwargs`` instead.
- Removed support for formset_kwarg ``save_as_new`` being set on
  ``BaseInlineFormSetMixin`` and its subclasses. Use
  ``BaseInlineFormSetMixin.formset_kwargs`` instead.
- Removed support for ``get_extra_form_kwargs``. This can be set in the
  dictionary key ``form_kwargs`` in ``BaseFormSetMixin.formset_kwargs`` instead.

0.10.0 (2018-02-28)
------------------
New features:

- Added SuccessMessageWithInlinesMixin (#151)
- Allow the formset prefix to be overridden (#154)

Bug fixes:

- SearchableMixin: Fix reduce() of empty sequence error (#149)
- Add fields attributes (Issue #144, PR #150)
- Fix Django 1.11 AttributeError: This QueryDict instance is immutable (#156)

0.9.0 (2017-03-08)
------------------
This version supports Django 1.7, 1.8, 1.9, 1.10 (latest minor versions), and Python 2.7, 3.4, 3.5 (latest minor versions).

- Added Django 1.10 support
- Dropped Django 1.6 support

0.8 (2016-06-14)
----------------

This version supports Django 1.6, 1.7, 1.8, 1.9 (latest minor versions), and Python 2.7, 3.4, 3.5 (latest minor versions).

- Added ``widgets`` attribute setting; allow to change form widgets in the ``ModelFormSetView``.
- Added Django 1.9 support.
- Fixed ``get_context_data()`` usage of ``*args, **kwargs``.
- Fixed silent overwriting of ``ModelForm`` fields to ``__all__``.


Backwards-incompatible changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Dropped support for Django <= 1.5 and Python 3.3.
- Removed the ``extra_views.multi`` module as it had neither documentation nor
  test coverage and was broken for some of the supported Django/Python versions.
- This package no longer implicitly set ``fields = '__all__'``.
  If you face ``ImproperlyConfigured`` exceptions, you should have a look at the
  `Django 1.6 release notes`_ and set the ``fields`` or ``exclude`` attributes
  on your ``ModelForm`` or extra-views views.

.. _Django 1.6 release notes: https://docs.djangoproject.com/en/stable/releases/1.6/#modelform-without-fields-or-exclude


0.7.1 (2015-06-15)
------------------
Beginning of this changelog.
