from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    profile_picture = models.URLField(null=True, blank=True)
    resume = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)


class JobApplication(models.Model):

    STATUS_CHOICES = [
        ("applied", "Applied"),
        ("interview", "Interview"),
        ("selected", "Selected"),
        ("rejected", "Rejected"),
    ]

    WORK_TYPE_CHOICES = [
        ("remote", "Remote"),
        ("hybrid", "Hybrid"),
        ("onsite", "On-site"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="job_applications"
    )

    role = models.CharField(max_length=200)

    company = models.CharField(max_length=200)

    stipend = models.CharField(max_length=100)

    location = models.CharField(max_length=200)

    work_type = models.CharField(
        max_length=20,
        choices=WORK_TYPE_CHOICES
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="applied"
    )

    applied_at = models.DateTimeField(auto_now_add=True)