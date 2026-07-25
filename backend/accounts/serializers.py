from rest_framework import serializers           # Import serializer classes
from .models import employee                     # Import employee model


class EmployeeSerializer(serializers.ModelSerializer):   # Serializer for employee model

    class Meta:                                  # Serializer configuration
        model = employee                         # Model associated with this serializer
        fields = "__all__"                       # Include all model fields