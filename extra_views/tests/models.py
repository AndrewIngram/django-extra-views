from django.db import models

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

class Item(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=13)
    price = models.DecimalField(decimal_places=2, max_digits=12, db_index=True)
    order = models.ForeignKey(Order)
    status = models.SmallIntegerField(default=0, choices=STATUS_CHOICES, db_index=True)
