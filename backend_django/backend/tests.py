from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import User, Service, Resource, Slot, Booking, WorkingHours
from .serializers import BookingSerializer
from datetime import datetime, timedelta
from django.utils import timezone


class ConsistencyTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@test.com", password="password")
        self.organiser = User.objects.create_user(
            email="org@test.com", password="password", role="organiser"
        )
        self.service = Service.objects.create(
            organiser=self.organiser,
            name="Test Service",
            duration_minutes=60,
        )
        self.resource = Resource.objects.create(
            service=self.service,
            name="Test Resource",
            type="user",
        )
        
        start = timezone.now() + timedelta(days=1)
        self.slot = Slot.objects.create(
            service=self.service,
            resource=self.resource,
            start_datetime=start,
            end_datetime=start + timedelta(minutes=60),
        )

    def test_booking_model_consistency(self):
        # Good booking
        booking = Booking(
            customer=self.user,
            service=self.service,
            resource=self.resource,
            slot=self.slot,
        )
        booking.clean()  # Should pass

        # Mismatched service
        other_service = Service.objects.create(
            organiser=self.organiser, name="Other", duration_minutes=30
        )
        booking.service = other_service
        with self.assertRaises(ValidationError):
            booking.clean()
            
    def test_booking_serializer_auto_assignment(self):
        # We simulate a request context
        from rest_framework.request import Request
        from rest_framework.test import APIRequestFactory
        
        factory = APIRequestFactory()
        request = factory.post('/')
        request.user = self.user
        
        data = {
            "slot": str(self.slot.id),
            # service and resource are NOT sent
        }
        
        serializer = BookingSerializer(data=data, context={"request": request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        booking = serializer.save()
        
        self.assertEqual(booking.service, self.service)
        self.assertEqual(booking.resource, self.resource)
        
    def test_working_hours_consistency(self):
        wh = WorkingHours(
            service=self.service,
            resource=self.resource,
            day_of_week=0,
            start_time="09:00",
            end_time="17:00",
        )
        wh.clean() # pass

        other_service = Service.objects.create(
            organiser=self.organiser, name="Other", duration_minutes=30
        )
        wh.service = other_service
        with self.assertRaises(ValidationError):
            wh.clean()
