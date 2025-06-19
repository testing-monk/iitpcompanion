from django.db import models
from Webusers.models import Users

class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]

    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    date = models.DateField()
    event_type = models.CharField(max_length=10, choices=EVENT_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.date})"
