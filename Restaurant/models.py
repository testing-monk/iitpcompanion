from django.db import models, transaction
from django.utils import timezone
from autoslug.fields import AutoSlugField
from Webusers.models import Users
from django.contrib.auth.hashers import make_password, check_password


class RegisterOwner(models.Model):
    ownername = models.CharField(max_length=50, null=False, unique=True)
    password = models.CharField(max_length=125, null=False)
    email = models.CharField(max_length=50, null=False, default=None)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def save(self, *args, **kwargs):
        # Auto-hash password only if not already hashed
        if not self.password.startswith('pbkdf2_'):
            self.set_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.ownername


class RegisterCanteen(models.Model):
    owner = models.ForeignKey(RegisterOwner, on_delete=models.CASCADE, related_name='restaurant_owner')
    canteen_name = models.CharField(max_length=100, default=None)
    description = models.TextField(default=None)
    image = models.ImageField(upload_to='canteen_images/')
    mobile_number = models.CharField(max_length=15)
    address = models.TextField()
    canteen_id = models.CharField(max_length=50, unique=True)
    opening_time = models.TimeField(default="07:00")
    closing_time = models.TimeField(default="22:00")
    email = models.EmailField()
    delivery_time = models.CharField(max_length=15, null=True, default="20 min")
    slug = AutoSlugField(populate_from='canteen_name', unique=True, always_update=False)

    def __str__(self):
        return self.canteen_name


class MenuItem(models.Model):
    canteen = models.ForeignKey(RegisterCanteen, on_delete=models.CASCADE, related_name='menu_items')
    category = models.CharField(max_length=100, default="Main Meal")
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='menu_images/',default="/menu_items/set-vector.jpg")
    delivery_time = models.CharField(max_length=15, null=True, default="20 min")
    slug = AutoSlugField(populate_from='name', unique=True, always_update=False)

    def __str__(self):
        return f"{self.name} - ₹{self.price}"


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

    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='orders')
    canteen = models.ForeignKey(RegisterCanteen, on_delete=models.CASCADE, related_name="orders")
    mobile_number = models.CharField(max_length=15, null=True, blank=True)
    items = models.JSONField(default=list)  # e.g., [{"name": "Pizza", "qty": 2}]
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
