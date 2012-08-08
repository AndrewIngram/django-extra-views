from calendar import Calendar
from collections import defaultdict
import datetime
import math

from django.views.generic.dates import DateMixin, YearMixin, MonthMixin, _date_from_string
from django.views.generic.list import MultipleObjectTemplateResponseMixin, BaseListView
from django.db. models import Q
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

DAYS = (
    _(u'Monday'),
    _(u'Tuesday'),
    _(u'Wednesday'),
    _(u'Thursday'),
    _(u'Friday'),
    _(u'Saturday'),
    _(u'Sunday'),
)

class BaseCalendarMonthView(DateMixin, YearMixin, MonthMixin, BaseListView):
    first_of_week = 0  # 0 = Monday, 6 = Sunday
    paginate_by = None  # We don't want to use this part of MultipleObjectMixin
    date_field = None
    end_date_field = None  # For supporting events with duration

    def get_paginate_by(self, queryset):
        if self.paginate_by is not None:
            raise ImproperlyConfigured(u"'%s' cannot be paginated, it is a calendar view" % self.__class__.__name__)
        return None

    def get_allow_future(self):
        return True

    def get_end_date_field(self):
        return self.end_date_field

    def get_first_of_week(self):
        if self.first_of_week is None:
            raise ImproperlyConfigured("%s.first_of_week is required." % self.__class__.__name__)
        return self.first_of_week

    def get_queryset(self):
        qs = super(BaseCalendarMonthView, self).get_queryset()

        year = self.get_year()
        month = self.get_month()

        date_field = self.get_date_field()
        end_date_field = self.get_end_date_field()

        date = _date_from_string(year, self.get_year_format(),
                                 month, self.get_month_format())

        since = date
        until = self.get_next_month(date)

        # Adjust our start and end dates to allow for next and previous
        # month edges
        if since.weekday() != self.get_first_of_week():
            diff = math.fabs(since.weekday() - self.get_first_of_week())
            since = since - datetime.timedelta(days=diff)

        if until.weekday() != ((self.get_first_of_week() + 6) % 7):
            diff = math.fabs(((self.get_first_of_week() + 6) % 7) - until.weekday())
            until = until + datetime.timedelta(days=diff)

        if end_date_field:
            # 5 possible conditions for showing an event:

            # 1) Single day event, starts after 'since'
            # 2) Multi-day event, starts after 'since' and ends before 'until'
            # 3) Starts before 'since' and ends after 'since' and before 'until'
            # 4) Starts after 'since' but before 'until' and ends after 'until'
            # 5) Starts before 'since' and ends after 'until'
            predicate1 = Q(**{
                '%s__gte' % date_field: since,
                end_date_field: None
            })
            predicate2 = Q(**{
                '%s__gte' % date_field: since,
                '%s__lt' % end_date_field: until
            })
            predicate3 = Q(**{
                '%s__lt' % date_field: since,
                '%s__gte' % end_date_field: until,
                '%s__lt' % end_date_field: until
            })
            predicate4 = Q(**{
                '%s__gte' % date_field: since,
                '%s__lt' % date_field: since,
                '%s__gte' % end_date_field: until
            })
            predicate5 = Q(**{
                '%s__lt' % date_field: since,
                '%s__gte' % end_date_field: until
            })
            return qs.filter(predicate1 | predicate2 | predicate3| predicate4 | predicate5)
        return qs.filter(**{
            '%s__gte' % date_field: since
        })

    def get_context_data(self, **kwargs):
        data = super(BaseCalendarMonthView, self).get_context_data(**kwargs)

        year = self.get_year()
        month = self.get_month()

        date = _date_from_string(year, self.get_year_format(),
                                 month, self.get_month_format())

        cal = Calendar(self.get_first_of_week())

        month_calendar = []
        now = datetime.datetime.utcnow()

        date_lists = defaultdict(list)

        for obj in data['object_list']:
            obj_date = getattr(obj, self.get_date_field())
            try:
                obj_date = obj_date.date()
            except AttributeError:
                # It's a date rather than datetime, so we use it as is
                pass
            date_lists[obj_date].append(obj)

        for week in cal.monthdatescalendar(date.year, date.month):
            week_calendar = []
            for day in week:
                week_calendar.append({
                    'day': day,
                    'object_list': date_lists[day],
                    'today': day == now.date(),
                    'is_current_month': day.month == date.month,
                })
            month_calendar.append(week_calendar)

        data['calendar'] = month_calendar
        data['weekdays'] = [DAYS[x] for x in cal.iterweekdays()]

        return data


class CalendarMonthView(MultipleObjectTemplateResponseMixin, BaseCalendarMonthView):
    template_name_suffix = '_calendar_month'
