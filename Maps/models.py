from django.db import models

class Map(models.Model):
    CATEGORY_CHOICES = [
        ('bus', 'Bus Route'),
        ('train', 'Train Map'),
        ('campus', 'Campus Map'),
        ('other', 'Other')
    ]

    title = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    image = models.ImageField(upload_to='maps/')
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"
