import datetime
try:
    from django.utils.timezone import now
except ImportError:
    now = datetime.datetime.now
import django
from django.db import models
from django.contrib.contenttypes.models import ContentType

if django.VERSION < (1, 8):
    from django.contrib.contenttypes.generic import GenericForeignKey
else:
    from django.contrib.contenttypes.fields import GenericForeignKey

STATUS_CHOICES = (
    (0, 'Placed'),
    (1, 'Charged'),
    (2, 'Shipped'),
    (3, 'Cancelled'),
)


class Order(models.Model):
    name = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    action_on_save = models.BooleanField(default=False)


class Item(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=13)
    price = models.DecimalField(decimal_places=2, max_digits=12, db_index=True)
    order = models.ForeignKey(Order, related_name='items')
    status = models.SmallIntegerField(default=0, choices=STATUS_CHOICES, db_index=True)
    date_placed = models.DateField(default=now, null=True, blank=True)

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.sku)


class Tag(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField()

    def __unicode__(self):
        return self.name
