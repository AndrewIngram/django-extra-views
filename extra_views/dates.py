from django.views.generic.dates import BaseMonthArchiveView
from django.views.generic.list import MultipleObjectTemplateResponseMixin
from calendar import Calendar
from collections import defaultdict
import datetime

class BaseCalendarMonthArchiveView(BaseMonthArchiveView):
    first_of_week = 0  # 0 = Monday, 6 = Sunday
    
    def get_context_data(self, **kwargs):
        data = super(BaseCalendarMonthArchiveView, self).get_context_data(**kwargs)
        date = data['date_list'][0]
        
        cal = Calendar(self.first_of_week)

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
                })
            month_calendar.append(week_calendar)
            
        data['calendar'] = month_calendar

        return data
    

class CalendarMonthArchiveView(MultipleObjectTemplateResponseMixin, BaseCalendarMonthArchiveView):
    template_name_suffix = '_calendar_month'