from django.db import models

class Assignment(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('pending', 'Pending'),
    ]

    subject = models.CharField(max_length=255,null=True, default='General')
    title = models.CharField(max_length=255)
    due_start = models.DateTimeField()
    due_end = models.DateTimeField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title
