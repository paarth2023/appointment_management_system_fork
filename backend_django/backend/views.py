from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Count, Q
import datetime

from .models import Service, Resource, Schedule, Booking, Notification
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    ServiceSerializer,
    ResourceSerializer,
    ScheduleSerializer,
    BookingSerializer,
    NotificationSerializer
)

User = get_user_model()


# --- Authentication ---

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


# --- Service & Resource Management (Organizer) ---

class IsOrganiserOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['organiser', 'admin']

class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.role == 'organiser':
            return Service.objects.filter(organiser=self.request.user)
        return Service.objects.filter(is_published=True)

    def perform_create(self, serializer):
        serializer.save(organiser=self.request.user)


class ResourceViewSet(viewsets.ModelViewSet):
    serializer_class = ResourceSerializer
    permission_classes = [IsOrganiserOrAdmin]
    queryset = Resource.objects.all()


class ScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = ScheduleSerializer
    permission_classes = [IsOrganiserOrAdmin]
    queryset = Schedule.objects.all()


# --- Booking (Customer) ---

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Booking.objects.all()
        elif user.role == 'organiser':
            # Organiser sees bookings for their services
            return Booking.objects.filter(service__organiser=user)
        else:
            # Customer sees their own bookings
            return Booking.objects.filter(customer=user)

    def create(self, request, *args, **kwargs):
        # Add basic availability check here if needed
        # For hackathon MVP, assuming frontend checks slots or we trust the input
        return super().create(request, *args, **kwargs)


class AvailabilityView(APIView):
    """
    Get available slots for a given service and date
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, service_id, date_str):
        try:
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            day_of_week = date.weekday()
            
            service = Service.objects.get(id=service_id)
            
            # Get general service schedule
            schedules = Schedule.objects.filter(
                service=service, 
                day_of_week=day_of_week, 
                is_active=True,
                resource__isnull=True
            )
            
            slots = []
            for sched in schedules:
                start = sched.start_time
                end = sched.end_time
                # Generate slots based on service duration
                # This is a simplified logic, real logic would iterate time chunks
                slots.append({
                    "start": start,
                    "end": end,
                    "available": True # simplified
                })
                
            return Response(slots)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


# --- Dashboard / Stats ---

class DashboardStatsView(APIView):
    permission_classes = [IsOrganiserOrAdmin]

    def get(self, request):
        user = request.user
        if user.role == 'admin':
            stats = {
                "total_users": User.objects.count(),
                "total_services": Service.objects.count(),
                "total_bookings": Booking.objects.count(),
            }
        else:
            # Organiser stats
            services = Service.objects.filter(organiser=user)
            stats = {
                "my_services": services.count(),
                "my_bookings": Booking.objects.filter(service__in=services).count(),
                "pending_bookings": Booking.objects.filter(service__in=services, status='pending').count()
            }
        return Response(stats)
