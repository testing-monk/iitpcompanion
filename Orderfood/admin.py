from django.contrib import admin
from .models import Canteen, MenuItem
from .models import OrderDetails

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



@admin.register(OrderDetails)
class OrderDetailsAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'mobile_number',
        'total_price',
        'order_type',
        'payment_type',
        'order_status',
        'ordered_at'
    )
    list_filter = ('order_status', 'order_type', 'payment_type')
    search_fields = ('user__username', 'mobile_number', 'items')

    readonly_fields = (
        'user',
        'mobile_number',
        'items',
        'total_price',
        'quantity',
        'address',
        'order_type',
        'payment_type',
        'ordered_at',
    )

    fields = (
        'user',
        'mobile_number',
        'items',
        'quantity',
        'total_price',
        'address',
        'order_type',
        'payment_type',
        'order_status',
        'ordered_at',
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return True
