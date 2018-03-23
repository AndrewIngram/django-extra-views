Miscellaneous
=============

formset_class
-------------

The :code:`formset_class` option should be used if you intend to customize your
:code:`InlineFormSet` and its associated formset methods.

As the :code:`InlineFormSet` isn't actually a sub-class of the Django
`BaseInlineFormSet <https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#django.forms.models.BaseInlineFormSet>`_, to achieve that, you need to define your own formset
class which extends the Django :code:`BaseInlineFormSet`.

For example, imagine you'd like to add your custom :code:`clean` method
for a formset. Then, define a custom formset class, a subclass of Django
:code:`BaseInlineFormSet`, like this::

    from django.db import models

    class MyCustomInlineFormSet(BaseInlineFormSet):

        def clean(self):
            # ...
            # Your custom clean logic goes here


Now, in your :code:`InlineFormSet` sub-class, use your formset class via
:code:`formset_class` setting, like this::

    from extra_views import InlineFormSet

    class MyInlineFormSet(InlineFormSet):
        model = SomeModel
        form_class = SomeForm
        formset_class = MyCustomInlineFormSet     # enables our custom inline

This will enable :code:`clean` method being executed on your
:code:`MyInLineFormSet`.
