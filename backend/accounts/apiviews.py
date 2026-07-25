from rest_framework.decorators import api_view          # Makes this function a DRF API
from rest_framework.response import Response             # Returns JSON response
from rest_framework import status                        # Gives HTTP status codes

from .models import employee                           # Import Employee model
from .serializers import EmployeeSerializer             # Import serializer


@api_view(["GET", "POST"])                              # Allow both GET and POST requests
def employees(request):

    if request.method == "GET":                         # If the request is GET

        employees = employee.objects.all()              # Fetch all employees

        serializer = EmployeeSerializer(
            employees,
            many=True                                   # many=True because multiple objects are returned
        )

        return Response(serializer.data)                # Return JSON


    elif request.method == "POST":                      # If the request is POST

        serializer = EmployeeSerializer(                # Create serializer using incoming JSON
            data=request.data
        )

        if serializer.is_valid():                       # Check whether JSON is valid

            serializer.save()                           # Save employee into PostgreSQL

            return Response(
                serializer.data,                        # Return created employee
                status=status.HTTP_201_CREATED          # HTTP Status 201 = Created
            )

        return Response(
            serializer.errors,                          # Return validation errors
            status=status.HTTP_400_BAD_REQUEST          # HTTP Status 400 = Invalid input
        )