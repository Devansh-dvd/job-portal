from rest_framework import serializers
from .models import User, JobApplication, HiringTeam, InterviewBooking, Notification

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "profile_picture",
            "resume",
            "description",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = [
            "id",
            "user",
            "role",
            "company",
            "stipend",
            "location",
            "work_type",
            "status",
            "applied_at",
        ]
        read_only_fields = ["id", "user", "applied_at"]


class RegisterHiringTeamSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    team_name = serializers.CharField(max_length=200)
    team_unique_id = serializers.CharField(max_length=100)
    location = serializers.CharField(max_length=200)
    contact = serializers.CharField(max_length=200)
    website_link = serializers.URLField(required=False, allow_blank=True)
    logo = serializers.URLField(required=False, allow_blank=True)


class CreateJobSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    location = serializers.CharField(max_length=200)
    job_type = serializers.ChoiceField(
        choices=["Full-time", "Part-time", "Contract", "Remote", "Internship"]
    )
    salary = serializers.CharField(max_length=100, required=False, allow_blank=True)
    description = serializers.CharField()
    requirements = serializers.CharField(required=False, allow_blank=True)
    tags = serializers.CharField(max_length=500, required=False, allow_blank=True)


class CandidateSerializer(serializers.ModelSerializer):
    booked_interviews_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "profile_picture",
            "resume",
            "description",
            "date_joined",
            "booked_interviews_count",
        ]

    def get_booked_interviews_count(self, obj):
        return obj.booked_interviews.filter(status="scheduled").count()


class InterviewBookingSerializer(serializers.ModelSerializer):
    candidate_username = serializers.CharField(source="candidate.username", read_only=True)
    candidate_email = serializers.CharField(source="candidate.email", read_only=True)
    candidate_profile_picture = serializers.URLField(source="candidate.profile_picture", read_only=True)
    candidate_resume = serializers.URLField(source="candidate.resume", read_only=True)
    team_name = serializers.CharField(source="hiring_team.team_name", read_only=True)
    team_logo = serializers.URLField(source="hiring_team.logo", read_only=True)
    team_location = serializers.CharField(source="hiring_team.location", read_only=True)
    team_contact = serializers.CharField(source="hiring_team.contact", read_only=True)
    team_email = serializers.EmailField(source="hiring_team.email", read_only=True)
    team_website = serializers.URLField(source="hiring_team.website_link", read_only=True)

    class Meta:
        model = InterviewBooking
        fields = [
            "id",
            "hiring_team",
            "candidate",
            "candidate_username",
            "candidate_email",
            "candidate_profile_picture",
            "candidate_resume",
            "team_name",
            "team_logo",
            "team_location",
            "team_contact",
            "team_email",
            "team_website",
            "role",
            "interview_date",
            "interview_type",
            "duration_minutes",
            "meeting_link",
            "notes",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "hiring_team", "created_at"]


class NotificationSerializer(serializers.ModelSerializer):
    interview_details = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient",
            "title",
            "message",
            "notification_type",
            "related_interview",
            "interview_details",
            "is_read",
            "created_at",
        ]
        read_only_fields = ["id", "recipient", "created_at"]

    def get_interview_details(self, obj):
        if not obj.related_interview:
            return None
        iv = obj.related_interview
        return {
            "id": iv.id,
            "role": iv.role,
            "team_name": iv.hiring_team.team_name,
            "team_logo": iv.hiring_team.logo,
            "team_location": iv.hiring_team.location,
            "interview_date": iv.interview_date,
            "interview_type": iv.interview_type,
            "duration_minutes": iv.duration_minutes,
            "meeting_link": iv.meeting_link,
            "notes": iv.notes,
            "status": iv.status,
        }

