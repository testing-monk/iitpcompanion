from django.contrib import admin
from .models import Map

@admin.register(Map)
class MapAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'uploaded_at')
    search_fields = ('title', 'category')
    list_filter = ('category',)