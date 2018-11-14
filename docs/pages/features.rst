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
