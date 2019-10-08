import datetime

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

try:
    from django.utils.timezone import now
except ImportError:
    now = datetime.datetime.now


STATUS_CHOICES = ((0, "Placed"), (1, "Charged"), (2, "Shipped"), (3, "Cancelled"))


class Order(models.Model):
    name = models.CharField(max_length=255)
    customer = models.CharField(max_length=255, default="", blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    action_on_save = models.BooleanField(default=False)

    def get_absolute_url(self):
        return "/inlines/%i/" % self.pk

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=13)
    price = models.DecimalField(decimal_places=2, max_digits=12, db_index=True)
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    status = models.SmallIntegerField(default=0, choices=STATUS_CHOICES, db_index=True)
    date_placed = models.DateField(default=now, null=True, blank=True)

    def __str__(self):
        return "%s (%s)" % (self.name, self.sku)


class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    order = models.ForeignKey(Order, related_name="contacts", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField()

    def __str__(self):
        return self.name
