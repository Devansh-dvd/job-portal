from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, JobApplication, HiringTeam
from .serializers import UserSerializer, LoginSerializer, JobApplicationSerializer, RegisterHiringTeamSerializer

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


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def register_hiring_team(request):
    # Pull flat fields from multipart data
    data = request.data.dict()

    # Upload logo to Cloudinary if provided
    logo_url = ""
    logo_file = request.FILES.get("logo")
    if logo_file:
        result = cloudinary.uploader.upload(logo_file)
        logo_url = result["secure_url"]
    data["logo"] = logo_url

    serializer = RegisterHiringTeamSerializer(data=data)
    if serializer.is_valid():
        validated = serializer.validated_data

        if HiringTeam.objects.filter(team_unique_id=validated['team_unique_id']).exists():
            return Response(
                {"team_unique_id": ["This team ID is already taken."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=validated['email']).exists():
            return Response(
                {"email": ["A user with this email already exists."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        if HiringTeam.objects.filter(email=validated['email']).exists():
            return Response(
                {"email": ["A hiring team with this email already exists."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User(
            username=validated['team_unique_id'],
            email=validated['email'],
            is_hiring_team=True,
        )
        user.set_password(validated['password'])
        user.save()

        HiringTeam.objects.create(
            user=user,
            team_name=validated['team_name'],
            team_unique_id=validated['team_unique_id'],
            email=validated['email'],
            location=validated['location'],
            contact=validated['contact'],
            website_link=validated.get('website_link') or '',
            logo=logo_url,
        )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Hiring team registered successfully",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "team": {
                    "teamName": validated['team_name'],
                    "teamUniqueId": validated['team_unique_id'],
                    "location": validated['location'],
                    "contact": validated['contact'],
                    "websiteLink": validated.get('website_link') or '',
                    "logo": logo_url,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def login_hiring_team(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user_obj = User.objects.get(email=email, is_hiring_team=True)
        except User.DoesNotExist:
            return Response(
                {"message": "Invalid credentials or not a hiring team account."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = authenticate(username=user_obj.username, password=password)
        if user is None:
            return Response(
                {"message": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            team = user.hiring_team_profile
        except HiringTeam.DoesNotExist:
            return Response(
                {"message": "Hiring team profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Login successful",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "team": {
                    "teamName": team.team_name,
                    "teamUniqueId": team.team_unique_id,
                    "location": team.location,
                    "contact": team.contact,
                    "websiteLink": team.website_link or '',
                    "logo": team.logo or '',
                },
            },
            status=status.HTTP_200_OK,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)