Miscellaneous
=============

formset_class
-------------

The :code:`formset_class` option should be used if you intend to customize your
:code:`InlineFormSetFactory` and its associated formset methods.

For example, imagine you'd like to add your custom :code:`clean` method
for a formset. Then, define a custom formset class, a subclass of Django
:code:`BaseInlineFormSet`, like this::

    from django.forms.models import BaseInlineFormSet

    class MyCustomInlineFormSet(BaseInlineFormSet):

        def clean(self):
            # ...
            # Your custom clean logic goes here


Now, in your :code:`InlineFormSetFactory` sub-class, use your formset class via
:code:`formset_class` setting, like this::

    from extra_views import InlineFormSetFactory

    class MyInline(InlineFormSetFactory):
        model = SomeModel
        form_class = SomeForm
        formset_class = MyCustomInlineFormSet     # enables our custom inline

This will enable :code:`clean` method being executed on your :code:`MyInline`.
