from rest_framework import serializers
from .models import User, JobApplication, HiringTeam

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