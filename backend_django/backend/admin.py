from django.contrib import admin
from .models import (
    User,
    Service,
    Resource,
    WorkingHours,
    Slot,
    Booking,
    Payment,
    Notification,
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "full_name", "role", "is_verified", "is_active"]
    list_filter = ["role", "is_verified", "is_active"]
    search_fields = ["email", "full_name"]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["name", "organiser", "duration_minutes", "price", "is_published"]
    list_filter = ["is_published"]
    search_fields = ["name", "organiser__email"]


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ["name", "service", "type", "is_active"]
    list_filter = ["type", "is_active"]


@admin.register(WorkingHours)
class WorkingHoursAdmin(admin.ModelAdmin):
    list_display = ["service", "resource", "day_of_week", "start_time", "end_time"]
    list_filter = ["day_of_week"]


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ["service", "resource", "start_datetime", "capacity", "booked_count"]
    list_filter = ["is_active"]


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ["customer", "service", "slot", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["customer__email", "service__name"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["booking", "amount", "status", "provider", "created_at"]
    list_filter = ["status", "provider"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "channel", "is_sent", "created_at"]
    list_filter = ["channel", "is_sent"]
