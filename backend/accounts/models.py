from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    