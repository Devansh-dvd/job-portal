from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    
    