from django.contrib import admin
from .models import Canteen, MenuItem

class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1
    fields = ('name', 'category', 'price', 'image')

@admin.register(Canteen)
class CanteenAdmin(admin.ModelAdmin):
    list_display = ('name', 'canteen_id', 'mobile_number', 'email', 'opening_time', 'closing_time')
    search_fields = ('name', 'canteen_id', 'mobile_number', 'email')
    inlines = [MenuItemInline]

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'canteen', 'price', 'slug')
    search_fields = ('name', 'description', 'canteen__name')
    list_filter = ('category', 'canteen')
    readonly_fields = ('slug',)
