from django.db import models
from autoslug.fields import AutoSlugField


class Club(models.Model):
    name = models.CharField(max_length=100)
    slug = AutoSlugField(unique=True)
    tagline = models.CharField(max_length=255, blank=True)
    founded = models.DateField(null=True, blank=True)
    president = models.CharField(max_length=100, blank=True)
    member_count = models.PositiveIntegerField(default=0)

    banner_image = models.ImageField(upload_to='club_banners/', blank=True, null=True,default="/club_banners/default.jpg")
    description = models.TextField(help_text="You can use HTML for formatting")

    email = models.EmailField(blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)

    def __str__(self):
        return self.name


class ClubGalleryImage(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='club_gallery/')
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.club.name} Image"
