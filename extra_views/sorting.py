import functools
from django.core.exceptions import ImproperlyConfigured

class SortHelper(object):
    def __init__(self, request, sort_fields_aliases, sort_param_name, sort_type_param_name):
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


class SortableListMixin(object):
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
        self.sort_helper = SortHelper(self.request, self.get_sort_fields(), self.sort_param_name, self.sort_type_param_name)
        return self.sort_helper

    def _sort_queryset(self, queryset):
        helper = self.get_sort_helper()
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
        ctx = super(SortableListMixin, self).get_context_data(**kwargs)
        if hasattr(self, 'sort_helper'):
            ctx['sort_helper'] = self.sort_helper
        return ctx