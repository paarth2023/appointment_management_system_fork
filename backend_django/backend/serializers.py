from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Service, Resource, Schedule, Booking, Notification

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "full_name",
            "phone_no",
            "password",
            "confirm_password",
            "role",
            "notification_preference"
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        return User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            full_name=validated_data["full_name"],
            phone_no=validated_data.get("phone_no"),
            role=validated_data.get("role", "customer"),
            notification_preference=validated_data.get("notification_preference", "email")
        )


class LoginSerializer(TokenObtainPairSerializer):
    """JWT login response with user info"""

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = {
            "id": str(self.user.id),
            "email": self.user.email,
            "full_name": self.user.full_name,
            "role": self.user.role,
        }
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "full_name", "phone_no", "role", "avatar", "notification_preference"]
        read_only_fields = ["id", "email"]


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = "__all__"
        read_only_fields = ["id"]


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = "__all__"
        read_only_fields = ["id"]


class ServiceSerializer(serializers.ModelSerializer):
    resources = ResourceSerializer(many=True, read_only=True)
    schedules = ScheduleSerializer(many=True, read_only=True)
    organiser_name = serializers.CharField(source="organiser.full_name", read_only=True)

    class Meta:
        model = Service
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "organiser"]

    def create(self, validated_data):
        validated_data['organiser'] = self.context['request'].user
        return super().create(validated_data)


class BookingSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True)
    customer_name = serializers.CharField(source="customer.full_name", read_only=True)
    resource_name = serializers.CharField(source="resource.name", read_only=True, allow_null=True)

    class Meta:
        model = Booking
        fields = "__all__"
        read_only_fields = ["id", "customer", "created_at", "updated_at", "status"]

    def create(self, validated_data):
        validated_data['customer'] = self.context['request'].user
        return super().create(validated_data)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ["id", "created_at"]
