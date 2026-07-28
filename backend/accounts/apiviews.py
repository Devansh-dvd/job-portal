from rest_framework.decorators import api_view          # Makes this function a DRF API
from rest_framework.response import Response             # Returns JSON response
from rest_framework import status                        # Gives HTTP status codes

from .models import User
from .serializers import UserSerializer

@api_view(["GET", "POST"])
def users(request):

    if request.method == "GET":

        users = User.objects.all()

        serializer = UserSerializer(
            users,
            many=True
        )

        return Response(serializer.data)

    elif request.method == "POST":

        serializer = UserSerializer(
            data=request.data
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )