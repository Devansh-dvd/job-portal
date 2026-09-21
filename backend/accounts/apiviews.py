from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from django.db.models import Q
from .models import User, JobApplication, HiringTeam, InterviewBooking
from .serializers import (
    UserSerializer,
    LoginSerializer,
    JobApplicationSerializer,
    RegisterHiringTeamSerializer,
    CandidateSerializer,
    InterviewBookingSerializer,
)

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
        result_resume = cloudinary.uploader.upload(resume, resource_type="raw")
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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    if user.is_hiring_team:
        team_data = None
        try:
            team = user.hiring_team_profile
            team_data = {
                "teamName": team.team_name,
                "teamUniqueId": team.team_unique_id,
                "email": team.email,
                "location": team.location,
                "contact": team.contact,
                "websiteLink": team.website_link or "",
                "logo": team.logo or "",
            }
        except HiringTeam.DoesNotExist:
            pass

        return Response(
            {
                "type": "hiring_team",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "profile_picture": user.profile_picture,
                    "resume": user.resume,
                    "description": user.description,
                },
                "team": team_data,
            },
            status=status.HTTP_200_OK,
        )

    return Response(
        {
            "type": "user",
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


@api_view(["GET"])
def list_candidates(request):
    """
    Returns candidate users (is_hiring_team=False).
    Supports ?search= keyword query across username, email, description.
    If requested by an authenticated hiring team, also attaches booking info.
    """
    search = request.GET.get("search", "").strip()
    candidates = User.objects.filter(is_hiring_team=False)

    if search:
        candidates = candidates.filter(
            Q(username__icontains=search)
            | Q(email__icontains=search)
            | Q(description__icontains=search)
        )

    candidates = candidates.order_by("-date_joined")

    current_team = None
    if request.user.is_authenticated and getattr(request.user, "is_hiring_team", False):
        try:
            current_team = request.user.hiring_team_profile
        except HiringTeam.DoesNotExist:
            current_team = None

    results = []
    for c in candidates:
        candidate_data = {
            "id": c.id,
            "username": c.username,
            "email": c.email,
            "profile_picture": c.profile_picture,
            "resume": c.resume,
            "description": c.description,
            "date_joined": c.date_joined,
            "has_booked_interview": False,
            "latest_interview": None,
        }

        if current_team:
            latest_booking = (
                InterviewBooking.objects.filter(
                    hiring_team=current_team,
                    candidate=c,
                    status="scheduled",
                )
                .order_by("-interview_date")
                .first()
            )
            if latest_booking:
                candidate_data["has_booked_interview"] = True
                candidate_data["latest_interview"] = {
                    "id": latest_booking.id,
                    "role": latest_booking.role,
                    "interview_date": latest_booking.interview_date,
                    "interview_type": latest_booking.interview_type,
                    "duration_minutes": latest_booking.duration_minutes,
                    "meeting_link": latest_booking.meeting_link,
                    "notes": latest_booking.notes,
                    "status": latest_booking.status,
                }

        results.append(candidate_data)

    return Response(results, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_interview_booking(request):
    """
    Allows a logged-in hiring team to schedule an interview with a candidate.
    """
    user = request.user
    if not getattr(user, "is_hiring_team", False):
        return Response(
            {"message": "Only hiring teams can schedule interviews."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        team = user.hiring_team_profile
    except HiringTeam.DoesNotExist:
        return Response(
            {"message": "Hiring team profile not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    candidate_id = request.data.get("candidate_id") or request.data.get("candidate")
    role = (request.data.get("role") or "").strip()
    interview_date = request.data.get("interview_date")
    interview_type = request.data.get("interview_type") or "Technical Round"
    duration_minutes = request.data.get("duration_minutes") or 45
    meeting_link = (request.data.get("meeting_link") or "").strip()
    notes = (request.data.get("notes") or "").strip()

    if not candidate_id:
        return Response(
            {"message": "Candidate ID is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not role:
        return Response(
            {"message": "Job role/position is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not interview_date:
        return Response(
            {"message": "Interview date and time are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        candidate = User.objects.get(id=candidate_id, is_hiring_team=False)
    except User.DoesNotExist:
        return Response(
            {"message": "Candidate not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        duration_int = int(duration_minutes)
    except (TypeError, ValueError):
        duration_int = 45

    booking = InterviewBooking.objects.create(
        hiring_team=team,
        candidate=candidate,
        role=role,
        interview_date=interview_date,
        interview_type=interview_type,
        duration_minutes=duration_int,
        meeting_link=meeting_link or None,
        notes=notes or None,
        status="scheduled",
    )

    serializer = InterviewBookingSerializer(booking)
    return Response(
        {
            "message": f"Interview scheduled successfully with {candidate.username}!",
            "booking": serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_interviews(request):
    """
    Returns all interviews booked by the authenticated hiring team.
    """
    user = request.user
    if not getattr(user, "is_hiring_team", False):
        return Response(
            {"message": "Only hiring teams can access scheduled interviews."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        team = user.hiring_team_profile
    except HiringTeam.DoesNotExist:
        return Response(
            {"message": "Hiring team profile not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    interviews = InterviewBooking.objects.filter(hiring_team=team).order_by("-interview_date")
    serializer = InterviewBookingSerializer(interviews, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)