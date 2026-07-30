from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import parser_classes

from .serializers import UserSerializer

@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def register(request):
    serializer = UserSerializer(data=request.data)

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