from django.db import models, transaction
from django.utils import timezone
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
    delivery_time = models.CharField(max_length=15, null=True, default="20 min")
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
    delivery_time = models.CharField(max_length=15, null=True, default="20 min")
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


class OrderDetails(models.Model):
    ORDER_TYPE_CHOICES = [
        ('Delivery', 'Delivery'),
        ('Pickup', 'Pickup'),
    ]

    PAYMENT_TYPE_CHOICES = [
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('Online', 'Online'),
    ]

    ORDER_STATUS_CHOICES = [
        ('Confirmed', 'Confirmed'),
        ('Rejected', 'Rejected'),
        ('Ready', 'Ready'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
        ('Pending', 'Pending'),
    ]

    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=15, null=True, blank=True)
    items = models.TextField(help_text="Comma-separated list of item names")
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField()
    address = models.TextField()
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    order_status = models.CharField(max_length=30, choices=ORDER_STATUS_CHOICES, default='Pending')
    ordered_at = models.DateTimeField(default=timezone.now)
    order_number = models.CharField(max_length=20, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            with transaction.atomic():
                year = timezone.now().year
                last_order = OrderDetails.objects.filter(
                    order_number__startswith=f"ORD-{year}"
                ).order_by('-id').first()

                last_number = 0
                if last_order and last_order.order_number:
                    try:
                        last_number = int(last_order.order_number.split('-')[-1])
                    except ValueError:
                        pass
                self.order_number = f"ORD-{year}-{last_number + 1:06d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order by {self.user.username} - {self.order_status}"
