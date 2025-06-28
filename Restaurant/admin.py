from django.contrib import admin
from .models import RegisterOwner, RegisterCanteen, MenuItem, OrderDetails


@admin.register(RegisterOwner)
class RegisterOwnerAdmin(admin.ModelAdmin):
    list_display = ('ownername', 'email')
    search_fields = ('ownername', 'email')
    ordering = ('ownername',)

    fieldsets = (
        (None, {
            'fields': ('ownername', 'email', 'password'),
            'description': "Note: The password is securely hashed before saving."
        }),
    )


@admin.register(RegisterCanteen)
class RegisterCanteenAdmin(admin.ModelAdmin):
    list_display = ('canteen_name', 'owner', 'mobile_number', 'email', 'opening_time', 'closing_time')
    list_filter = ('opening_time', 'closing_time')
    search_fields = ('canteen_name', 'owner__ownername')
    ordering = ('canteen_name',)

    fieldsets = (
        ('Canteen Details', {
            'fields': (
                'canteen_name', 'description', 'image'
            )
        }),
        ('Owner Info', {
            'fields': ('owner', 'canteen_id', 'email', 'mobile_number')
        }),
        ('Address & Timing', {
            'fields': ('address', 'opening_time', 'closing_time', 'delivery_time')
        }),
    )


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'canteen', 'category', 'price', 'delivery_time')
    list_filter = ('canteen', 'category')
    search_fields = ('name', 'canteen__canteen_name')
    ordering = ('canteen', 'name')

    fields = (
        'canteen',
        'category',
        'name',
        'description',
        'price',
        'image',
        'delivery_time',
    )


@admin.register(OrderDetails)
class OrderDetailsAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 'user', 'canteen', 'total_price', 'quantity',
        'order_status', 'ordered_at'
    )
    list_filter = ('order_status', 'ordered_at', 'canteen')
    search_fields = ('order_number', 'user__username', 'canteen__canteen_name')
    ordering = ('-ordered_at',)
    readonly_fields = ('order_number', 'ordered_at')

    fieldsets = (
        ('Order Info', {
            'fields': (
                'order_number', 'user', 'canteen', 'mobile_number', 'address',
                'items', 'total_price', 'quantity'
            )
        }),
        ('Status & Timing', {
            'fields': ('order_type', 'payment_type', 'order_status', 'ordered_at')
        }),
    )
