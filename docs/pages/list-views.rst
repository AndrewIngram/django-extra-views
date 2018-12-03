List Views
==========

Searchable List Views
---------------------
You can add search functionality to your ListViews by adding SearchableListMixin
and by setting search_fields:

.. code-block:: python

    from django.views.generic import ListView
    from extra_views import SearchableListMixin

    class SearchableItemListView(SearchableListMixin, ListView):
        template_name = 'extra_views/item_list.html'
        search_fields = ['name', 'sku']
        model = Item

In this case ``object_list`` will be filtered if the 'q' query string is provided
(like /searchable/?q=query), or you can manually override ``get_search_query``
method, to define your own search functionality.

Also you can define some items  in ``search_fields`` as tuple (e.g.
``[('name', 'iexact', ), 'sku']``) to provide custom lookups for searching.
Default lookup is ``icontains``. We strongly recommend to use only string lookups,
when number fields will convert to strings before comparison to prevent converting errors.
This controlled by ``check_lookups`` setting of SearchableMixin.

Sortable List View
------------------

.. code-block:: python

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

