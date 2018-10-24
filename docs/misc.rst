Miscellaneous
=============

Overriding the formset_class
----------------------------

The :code:`formset_class` option should be used if you intend to customize your
subclass of :code:`BaseFormSetFactory` and its formset methods.

For example, imagine you'd like to add your custom :code:`clean` method
for an inline formset. Then, define a custom formset class, a subclass of
Django's :code:`BaseInlineFormSet`, like this::

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

This will enable :code:`clean` method being executed on your instance of
:code:`MyInline`.

Initial data for ModelFormSet and InlineFormSet
-----------------------------------------------

Passing initial data into ModelFormSet and InlineFormSet works slightly
differently to a regular FormSet. The data passed in from :code:`initial` will
be inserted into the :code:`extra` forms of the formset. Only the data from
:code:`get_queryset()` will be inserted into the initial rows::

    from extra_views import ModelFormSetView
    from foo.models import MyModel


    class MyModelFormSetView(ModelFormSetView):
        template_name = 'mymodelformset.html'
        model = MyModel
        factory_kwargs = {'extra': 10}
        initial = [{'name': 'foo'}, {'name': 'bar'}]

The above will result in a formset containing a form for each instance of
MyModel in the database, followed by 2 forms containing the extra initial data,
followed by 8 empty forms.

Passing arguments to the form constructor
-----------------------------------------

In order to change the arguments which are passed into each form within the
formset, this can be done by the 'form_kwargs' argument passed in to the FormSet
constructor. For example, to give every form an initial value of 'default_name'
in the 'name' field::

    from extra_views import InlineFormSetFactory

    class ItemInline(InlineFormSetFactory):
        model = Item
        formset_kwargs = {'form_kwargs': {'initial': {'name': 'default_name'}}

If these need to be modified at run time, it can be done by
:code:`get_formset_kwargs()`.::

    from extra_views import InlineFormSetFactory

    class ItemInline(InlineFormSetFactory):
        model = Item

        def get_formset_kwargs():
            kwargs = super(ItemInline, self).get_formset_kwargs()
            initial = get_some_initial_values()
            kwargs['form_kwargs'].update({'initial': initial}}
            return kwargs


Named formsets
--------------
If you want more control over the names of your formsets (as opposed to
iterating over :code:`inlines`), you can use :code:`NamedFormsetsMixin`::

    from extra_views import NamedFormsetsMixin

    class CreateOrderView(NamedFormsetsMixin, CreateWithInlinesView):
        model = Order
        inlines = [ItemInline, TagInline]
        inlines_names = ['Items', 'Tags']
        fields = '__all__'

Then use the appropriate names to render them in the html template::

    ...
    {{ Tags }}
    ...
    {{ Items }}
    ...


Searchable List Views
---------------------
You can add search functionality to your ListViews by adding SearchableListMixin
and by setting search_fields::

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

Sortable List View
------------------
::

    from django.views.generic import ListView
    from extra_views import SortableListMixin

    class SortableItemListView(SortableListMixin, ListView):
        sort_fields_aliases = [('name', 'by_name'), ('id', 'by_id'), ]
        model = Item

You can hide real field names in query string by define sort_fields_aliases
attribute (see example) or show they as is by define sort_fields.
SortableListMixin adds ``sort_helper`` variable of SortHelper class,
then in template you can use helper functions:
``{{ sort_helper.get_sort_query_by_FOO }}``,
``{{ sort_helper.get_sort_query_by_FOO_asc }}``,
``{{ sort_helper.get_sort_query_by_FOO_desc }}`` and
``{{ sort_helper.is_sorted_by_FOO }}``