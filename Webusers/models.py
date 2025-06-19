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