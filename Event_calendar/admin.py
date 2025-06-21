from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'event_type', 'created_at')
    list_filter = ('event_type', 'date')
