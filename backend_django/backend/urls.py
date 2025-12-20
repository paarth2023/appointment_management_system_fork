from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    LoginView,
    ProfileView,
    ServiceViewSet,
    ResourceViewSet,
    ScheduleViewSet,
    BookingViewSet,
    AvailabilityView,
    DashboardStatsView
)

router = DefaultRouter()
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'resources', ResourceViewSet, basename='resource')
router.register(r'schedules', ScheduleViewSet, basename='schedule')
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    # Auth
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    
    # Core Logic
    path('availability/<str:service_id>/<str:date_str>/', AvailabilityView.as_view(), name='availability'),
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    
    # Router
    path('', include(router.urls)),
]
