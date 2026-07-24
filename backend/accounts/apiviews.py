from rest_framework.decorators import api_view          # Makes this function a DRF API
from rest_framework.response import Response             # Returns JSON response

from .models import employee                           # Import Employee model
from .serializers import EmployeeSerializer             # Import serializer


@api_view(["GET"])                                      # Allow only GET requests
def employees(request):

    employees = employee.objects.all()                  # Fetch all employees from database

    serializer = EmployeeSerializer(                    # Convert Employee objects into JSON
        employees,
        many=True                                       
    )

    return Response(serializer.data)                    