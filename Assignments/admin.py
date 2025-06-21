from django.contrib import admin
from .models import Assignment

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'status', 'due_start', 'due_end')
    list_filter = ('priority', 'status')
    search_fields = ('title',)
