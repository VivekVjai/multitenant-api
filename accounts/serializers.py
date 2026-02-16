from rest_framework import serializers
from .models import User


class UserMeSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source="tenant.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "tenant",
            "tenant_name",
            "is_active",
        ]
