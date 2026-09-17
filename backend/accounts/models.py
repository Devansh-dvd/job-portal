from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    profile_picture = models.URLField(null=True, blank=True)
    resume = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_hiring_team = models.BooleanField(default=False)


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


class HiringTeam(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='hiring_team_profile'
    )
    team_name = models.CharField(max_length=200)
    team_unique_id = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    location = models.CharField(max_length=200)
    contact = models.CharField(max_length=200)
    website_link = models.URLField(null=True, blank=True)
    logo = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.team_name


class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ("Full-time", "Full-time"),
        ("Part-time", "Part-time"),
        ("Contract", "Contract"),
        ("Remote", "Remote"),
        ("Internship", "Internship"),
    ]

    hiring_team = models.ForeignKey(
        HiringTeam, on_delete=models.CASCADE, related_name="posted_jobs"
    )
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES, default="Full-time")
    salary = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    tags = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} @ {self.hiring_team.team_name}"


class InterviewBooking(models.Model):
    INTERVIEW_TYPE_CHOICES = [
        ("Screening", "Initial Screening"),
        ("Technical", "Technical Round"),
        ("Design", "System Design / Portfolio"),
        ("Culture", "Culture & Leadership"),
        ("Final", "Final Discussion"),
    ]

    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    hiring_team = models.ForeignKey(
        HiringTeam,
        on_delete=models.CASCADE,
        related_name="interview_bookings"
    )
    candidate = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="booked_interviews"
    )
    role = models.CharField(max_length=200)
    interview_date = models.DateTimeField()
    interview_type = models.CharField(max_length=50, default="Technical")
    duration_minutes = models.IntegerField(default=45)
    meeting_link = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="scheduled")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interview: {self.candidate.username} for {self.role} by {self.hiring_team.team_name}"