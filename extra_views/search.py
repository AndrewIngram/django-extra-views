from django.db.models import Q
import datetime
import operator
import re


class SearchableListMixin(object):
    """
    Filter queryset like a django admin search_fields does, but with little more intellegence:
    if self.search_split is set to True (by default) it will split query to words (by whatespace)
    try to convert each word to date with self.search_date_formats and then search each word in separate field
    e.g. with query 'foo bar' you can find object with obj.field1='foo' and obj.field2='bar'

    This class is designed be used with django.generic.ListView

    You could specify by query by self.query on get method (or anywhere before get_queryset)
    if self.query is not specifed this class will try to get 'q' key for request.GET (this can be disabled with search_use_q=False)
    """
    search_fields = ['id']
    search_date_fields = None
    search_date_formats = ['%d.%m.%y', '%d.%m.%Y']
    search_split = True
    search_use_q = True

    def get_words(self, query):
        if self.search_split:
            return query.split()
        return query

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

    def get(self, request, *args, **kwargs):
        if (not hasattr(self, 'query')) and (self.search_use_q):
            self.query = request.GET.get('q', '')
        return super(SearchableListMixin, self).get(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(SearchableListMixin, self).get_queryset()
        if self.query:
            w_qs = []
            for word in self.get_words(self.query):
                filters = [Q(**{'%s__icontains' % field_name:word}) for field_name in self.search_fields]
                if self.search_date_fields:
                    dt = self.try_convert_to_date(word)
                    if dt:
                        filters.extend([Q(**{field_name:dt}) for field_name in self.search_date_fields])
                w_qs.append(reduce(operator.or_, filters))
            qs = qs.filter(reduce(operator.and_, w_qs))
        return qs.distinct()