from rest_framework import serializers
from .models import User, JobApplication

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