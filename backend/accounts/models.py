from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    profile_picture = models.URLField(null=True, blank=True)
    resume = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)