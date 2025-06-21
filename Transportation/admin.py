from django.contrib import admin
from .models import Bus, Train, BusSchedule

@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'from_location',
        'to_location',
        'status',
        'departure_time',
        'arrival_time',
    )
    search_fields = ('name', 'from_location', 'to_location', 'status')
    list_filter = ('status',)


@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = (
        'number',
        'name',
        'from_location',
        'to_location',
        'platform',
        'status',
        'departure_time',
        'arrival_time',
        'frequency',
        'days_running',
    )
    search_fields = (
        'number',
        'name',
        'platform',
        'from_location',
        'to_location',
        'status',
        'days_running',
    )
    list_filter = (
        'platform',
        'status',
        'frequency',
        'days_running',
    )


@admin.register(BusSchedule)
class BusScheduleAdmin(admin.ModelAdmin):
    list_display = (
        'bus_name',
        'from_location',
        'to_location',
        'departure_time',
        'arrival_time',
        'frequency',
    )
    search_fields = ('bus_name', 'from_location', 'to_location')
    list_filter = ('frequency',)
