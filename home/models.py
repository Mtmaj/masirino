from django.db import models

# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    active = models.BooleanField(null=True)
    auth_link = models.CharField(max_length=255,null=True)
    recovery_link = models.CharField(max_length=255,null=True)