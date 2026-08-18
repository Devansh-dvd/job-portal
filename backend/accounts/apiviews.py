from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User , JobApplication
from .serializers import UserSerializer, LoginSerializer , JobApplicationSerializer

import cloudinary.uploader


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def register(request):

    data = request.data.dict()

    profile_picture = request.FILES.get("profile_picture")
    resume = request.FILES.get("resume")

    if profile_picture:
        result = cloudinary.uploader.upload(profile_picture)
        data["profile_picture"] = result["secure_url"]

    if resume:
        result_resume = cloudinary.uploader.upload(resume)
        data["resume"] = result_resume["secure_url"]

    serializer = UserSerializer(data=data)

    if serializer.is_valid():

        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        return Response(
            {
                "message": "User registered successfully",
                "access": access,
                "refresh": str(refresh),
                "user": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["POST"])
def login(request):

    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {
                    "message": "Invalid email or password"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        user = authenticate(
            username=user_obj.username,
            password=password
        )

        if user is None:
            return Response(
                {
                    "message": "Invalid email or password"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        return Response(
            {
                "message": "Login successful",
                "access": access,
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "profile_picture": user.profile_picture,
                    "resume": user.resume,
                    "description": user.description,
                },
            },
            status=status.HTTP_200_OK,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["POST"])
def create_application(request):

    serializer = JobApplicationSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(user=request.user)

        return Response(
            {
                "message": "Job application created successfully",
                "application": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )