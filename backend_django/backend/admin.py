from django.contrib import admin
from .models import User, Service, Resource, Schedule, Booking, Notification


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "email",
        "full_name",
        "role",
        "phone_no",
        "date_joined",
    ]
    list_filter = ["role", "date_joined"]
    search_fields = ["email", "full_name"]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "organiser",
        "duration",
        "price",
        "is_published",
    ]
    list_filter = ["is_published"]
    search_fields = ["name", "organiser__email"]


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ["name", "service", "type"]
    list_filter = ["type"]


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ["service", "day_of_week", "start_time", "end_time", "is_active"]
    list_filter = ["day_of_week", "is_active"]


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        "customer",
        "service",
        "start_time",
        "status",
        "created_at",
    ]
    list_filter = ["status", "created_at"]
    search_fields = ["customer__email", "service__name"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "type",
        "channel",
        "status",
        "created_at",
    ]
    list_filter = ["status", "channel"]
