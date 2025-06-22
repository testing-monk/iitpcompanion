from django.contrib import admin
from .models import Users, UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'roll_number', 'department', 'year', 'hostel')
    search_fields = ('user__username', 'roll_number', 'department')
    list_filter = ('year', 'hostel')

from django.contrib import admin
from .models import Users

@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email')
    search_fields = ('username', 'email')
    ordering = ('id',)
