from django.db import models

class Bus(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True, default=None)
    from_location = models.CharField(max_length=100, null=True, blank=True, default=None)
    to_location = models.CharField(max_length=100, null=True, blank=True, default=None)
    status = models.CharField(max_length=50, choices=[
        ('Arriving', 'Arriving'),
        ('On Route', 'On Route'),
        ('Delayed', 'Delayed'),
        ('On Time', 'On Time'),
    ], null=True, blank=True, default=None)
    departure_time = models.CharField(max_length=20, null=True, blank=True, default=None)
    arrival_time = models.CharField(max_length=20, null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.name} ({self.from_location} → {self.to_location})"


from django.db import models

class Train(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True, default=None)
    number = models.CharField(max_length=20, null=True, blank=True, default=None)
    platform = models.CharField(max_length=50, null=True, blank=True, default=None)
    from_location = models.CharField(max_length=100, null=True, blank=True, default=None)
    to_location = models.CharField(max_length=100, null=True, blank=True, default=None)
    status = models.CharField(max_length=50, choices=[
        ('Arriving', 'Arriving'),
        ('Delayed', 'Delayed'),
        ('On Time', 'On Time'),
    ], null=True, blank=True, default=None)
    departure_time = models.CharField(max_length=20, null=True, blank=True, default=None)
    arrival_time = models.CharField(max_length=20, null=True, blank=True, default=None)
    frequency = models.CharField(max_length=50, null=True, blank=True, default=None)
    days_running = models.CharField(max_length=100, null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.number or ''} {self.name or ''} ({self.from_location} → {self.to_location})"



class BusSchedule(models.Model):
    bus_name = models.CharField(max_length=100, null=True, blank=True, default=None)
    from_location = models.CharField(max_length=100, null=True, blank=True, default=None)
    to_location = models.CharField(max_length=100, null=True, blank=True, default=None)
    departure_time = models.CharField(max_length=20, null=True, blank=True, default=None)
    arrival_time = models.CharField(max_length=20, null=True, blank=True, default=None)
    frequency = models.CharField(max_length=50, null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.bus_name} ({self.from_location} → {self.to_location})"
