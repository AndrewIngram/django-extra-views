from __future__ import unicode_literals

import datetime
import functools
import operator

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q

import six
from six.moves import reduce

from ..compat import ContextMixin


VALID_STRING_LOOKUPS = (
    'iexact', 'contains', 'icontains', 'startswith', 'istartswith', 'endswith',
    'iendswith', 'search', 'regex', 'iregex')


class SearchableListMixin(object):
    """
    Filter queryset like a django admin search_fields does, but with little more intelligence:
    if self.search_split is set to True (by default) it will split query to words (by whitespace)
    Also tries to convert each word to date with self.search_date_formats and then search each word in separate field
    e.g. with query 'foo bar' you can find object with obj.field1__icontains='foo' and obj.field2__icontains=='bar'

    To provide custom lookup just set one of the search_fields to tuple,
    e.g. search_fields = [('field1', 'iexact'), 'field2', ('field3', 'startswith')]

    This class is designed to be used with django.generic.ListView

    You could specify query by overriding get_search_query method
    by default this method will try to get 'q' key from request.GET (this can be disabled with search_use_q=False)
    """
    search_fields = ['id']
    search_date_fields = None
    search_date_formats = ['%d.%m.%y', '%d.%m.%Y']
    search_split = True
    search_use_q = True
    check_lookups = True

    def get_words(self, query):
        if self.search_split:
            return query.split()
        return [query]

    def get_search_fields_with_filters(self):
        fields = []
        for sf in self.search_fields:
            if isinstance(sf, six.string_types):
                fields.append((sf, 'icontains', ))
            else:
                if self.check_lookups and sf[1] not in VALID_STRING_LOOKUPS:
                    raise ValueError('Invalid string lookup - %s' % sf[1])
                fields.append(sf)
        return fields

    def try_convert_to_date(self, word):
        """
        Tries to convert word to date(datetime) using search_date_formats
        Return None if word fits no one format
        """
        for frm in self.search_date_formats:
            try:
                return datetime.datetime.strptime(word, frm).date()
            except ValueError:
                pass
        return None

    def get_search_query(self):
        """
        Get query from request.GET 'q' parameter when search_use_q is set to True
        Override this method to provide your own query to search
        """
        return self.search_use_q and self.request.GET.get('q', '') or None

    def get_queryset(self):
        qs = super(SearchableListMixin, self).get_queryset()
        query = self.get_search_query()
        if query:
            w_qs = []
            search_pairs = self.get_search_fields_with_filters()
            for word in self.get_words(query):
                filters = [Q(**{'%s__%s' % (pair[0], pair[1]): word}) for pair in search_pairs]
                if self.search_date_fields:
                    dt = self.try_convert_to_date(word)
                    if dt:
                        filters.extend([Q(**{field_name: dt}) for field_name in self.search_date_fields])
                w_qs.append(reduce(operator.or_, filters))
            qs = qs.filter(reduce(operator.and_, w_qs))
            qs = qs.distinct()
        return qs


class SortHelper(object):
    def __init__(self, request, sort_fields_aliases, sort_param_name, sort_type_param_name):
        # Create a list from sort_fields_aliases, in case it is a generator,
        # since we want to iterate through it multiple times.
        sort_fields_aliases = list(sort_fields_aliases)

        self.initial_params = request.GET.copy()
        self.sort_fields = dict(sort_fields_aliases)
        self.inv_sort_fields = dict((v, k) for k, v in sort_fields_aliases)
        self.initial_sort = self.inv_sort_fields.get(self.initial_params.get(sort_param_name), None)
        self.initial_sort_type = self.initial_params.get(sort_type_param_name, 'asc')
        self.sort_param_name = sort_param_name
        self.sort_type_param_name = sort_type_param_name

        for field, alias in self.sort_fields.items():
            setattr(self, 'get_sort_query_by_%s' % alias, functools.partial(self.get_params_for_field, field))
            setattr(self, 'get_sort_query_by_%s_asc' % alias, functools.partial(self.get_params_for_field, field, 'asc'))
            setattr(self, 'get_sort_query_by_%s_desc' % alias, functools.partial(self.get_params_for_field, field, 'desc'))
            setattr(self, 'is_sorted_by_%s' % alias, functools.partial(self.is_sorted_by, field))

    def is_sorted_by(self, field_name):
        return field_name == self.initial_sort and self.initial_sort_type or False

    def get_params_for_field(self, field_name, sort_type=None):
        """
        If sort_type is None - inverse current sort for field, if no sorted - use asc
        """
        if not sort_type:
            if self.initial_sort == field_name:
                sort_type = 'desc' if self.initial_sort_type == 'asc' else 'asc'
            else:
                sort_type = 'asc'
        self.initial_params[self.sort_param_name] = self.sort_fields[field_name]
        self.initial_params[self.sort_type_param_name] = sort_type
        return '?%s' % self.initial_params.urlencode()

    def get_sort(self):
        if not self.initial_sort:
            return None
        sort = '%s' % self.initial_sort
        if self.initial_sort_type == 'desc':
            sort = '-%s' % sort
        return sort


class SortableListMixin(ContextMixin):
    """
    You can provide either sort_fields as a plain list like ['id', 'some', 'foo__bar', ...]
    or, if you want to hide original field names you can provide list of tuples with aliace that will be used:
    [('id', 'by_id'), ('some', 'show_this'), ('foo__bar', 'bar')]

    If sort_param_name exists in query but sort_type_param_name is omitted queryset will be sorted as 'asc'
    """
    sort_fields = []
    sort_fields_aliases = []
    sort_param_name = 'o'
    sort_type_param_name = 'ot'

    def get_sort_fields(self):
        if self.sort_fields:
            return zip(self.sort_fields, self.sort_fields)
        return self.sort_fields_aliases

    def get_sort_helper(self):
        return SortHelper(self.request, self.get_sort_fields(), self.sort_param_name, self.sort_type_param_name)

    def _sort_queryset(self, queryset):
        self.sort_helper = self.get_sort_helper()
        sort = self.sort_helper.get_sort()
        if sort:
            queryset = queryset.order_by(sort)
        return queryset

    def get_queryset(self):
        qs = super(SortableListMixin, self).get_queryset()
        if self.sort_fields and self.sort_fields_aliases:
            raise ImproperlyConfigured('You should provide sort_fields or sort_fields_aliaces but not both')
        return self._sort_queryset(qs)

    def get_context_data(self, **kwargs):
        context = {}
        if hasattr(self, 'sort_helper'):
            context['sort_helper'] = self.sort_helper
        context.update(kwargs)
        return super(SortableListMixin, self).get_context_data(**context)
