from django.db import models
from autoslug.fields import AutoSlugField

from Webusers.models import Users


class Canteen(models.Model):
    name = models.CharField(max_length=100, default=None)
    description = models.TextField(default=None)
    opening_time = models.TimeField(default="07:00")
    closing_time = models.TimeField(default="22:00")

    image = models.ImageField(upload_to='canteen_images/')
    mobile_number = models.CharField(max_length=15)
    address = models.TextField()
    canteen_id = models.CharField(max_length=50, unique=True)
    email = models.EmailField()
    delivery_time = models.CharField(max_length=15,null=True,default="20 min")
    slug = AutoSlugField(populate_from='name', unique=True, always_update=False)

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    canteen = models.ForeignKey(Canteen, on_delete=models.CASCADE, related_name='menu_items')
    category = models.CharField(max_length=100, default="Main Meal")
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='menu_images/')
    delivery_time = models.CharField(max_length=15,null=True,default="20 min")
    slug = AutoSlugField(populate_from='name', unique=True, always_update=False)

    def __str__(self):
        return f"{self.name} - ₹{self.price}"


class Cart(models.Model):
    cart_user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='cart_items')
    item_title = models.CharField(max_length=50, null=True, blank=True)
    item_price = models.IntegerField(null=True, blank=True)
    item_quantity = models.PositiveIntegerField(default=1)
    item_slug = models.SlugField(unique=True, null=False, default=None)

    def __str__(self):
        return self.item_title or "Cart Item"