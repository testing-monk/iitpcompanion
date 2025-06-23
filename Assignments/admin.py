from django.contrib import admin
from .models import Assignment
from django.utils.html import format_html

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('subject', 'title', 'priority', 'status', 'formatted_due_start', 'formatted_due_end', 'link')
    list_filter = ('priority', 'status')
    search_fields = ('subject', 'title', 'link')

    def formatted_due_start(self, obj):
        return obj.due_start.strftime('%a, %d %b %Y, %I:%M %p')
    formatted_due_start.short_description = 'Opened'

    def formatted_due_end(self, obj):
        return obj.due_end.strftime('%a, %d %b %Y, %I:%M %p')
    formatted_due_end.short_description = 'Due'
