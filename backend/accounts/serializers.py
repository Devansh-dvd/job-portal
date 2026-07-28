from rest_framework import serializers           # Import serializer classes
from .models import User                   # Import employee model


class UserSerializer(serializers.ModelSerializer):   # Serializer for employee model

    class Meta:                                  # Serializer configuration
        model = User                         # Model associated with this serializer
        fields = "__all__"                       # Include all model fields