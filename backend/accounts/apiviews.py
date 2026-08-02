from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import parser_classes
from .serializers import UserSerializer
import cloudinary.uploader  

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def register(request):

    data = request.data.copy()

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
        serializer.save()
        return Response(
            {
                "message": "User registered successfully",
                "user": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    print(serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)