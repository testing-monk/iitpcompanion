from django.contrib.auth.hashers import make_password, check_password
from django.db import models

class Users(models.Model):
    username=models.CharField(max_length=50,null=False,unique=True)
    password=models.CharField(max_length=125,null=False)
    email=models.CharField(max_length=50,null=False,default=None)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username



class UserProfile(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=20, null=True,default=None)
    department = models.CharField(max_length=100,null=True,default=None)
    year = models.IntegerField(choices=[(1, '1st'), (2, '2nd'), (3, '3rd'), (4, '4th')],null=True,default=None)
    hostel = models.CharField(max_length=100,null=True,default=None)
    profile_image = models.ImageField(upload_to='profile_images/', default='profile_images/default.png')
    mobile_number = models.CharField(max_length=15, blank=True,null=True,default=None)

    saved_foods = models.JSONField(default=list, blank=True)
    saved_routes = models.JSONField(default=list, blank=True)
    saved_assignments = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.user.username

