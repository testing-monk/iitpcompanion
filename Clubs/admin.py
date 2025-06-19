from django.contrib import admin
from .models import Club, ClubGalleryImage

class ClubGalleryInline(admin.TabularInline):
    model = ClubGalleryImage
    extra = 1

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'president', 'founded')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ClubGalleryInline]
