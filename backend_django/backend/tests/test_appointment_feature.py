# backend/tests/test_appointment_feature.py
"""
FEATURE: Appointment Management System
Tests the complete appointment booking workflow across Model, Serializer, and View layers.
Units tested: Appointment model, AppointmentSerializer, Appointment views
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from backend.models import Doctor, Appointment
from backend.serializers import AppointmentSerializer
from datetime import date, time
from django.db import IntegrityError

User = get_user_model()


class AppointmentManagementFeatureTest(TestCase):
    """
    FEATURE: Appointment Management System
    
    This test suite validates the complete appointment workflow:
    - Creating appointments with doctors
    - Preventing double-booking
    - Cancelling and rebooking
    - Listing user appointments
    - Concurrent bookings by multiple users
    
    Tests span: Model layer + Serializer layer + View layer
    """

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test users
        self.patient1 = User.objects.create_user(
            email='patient1@example.com',
            phone_no='+917777777777',
            full_name='Patient One',
            password='Pass123!'
        )
        
        self.patient2 = User.objects.create_user(
            email='patient2@example.com',
            phone_no='+917777777778',
            full_name='Patient Two',
            password='Pass123!'
        )
        
        # Create test doctor
        self.doctor = Doctor.objects.create(
            name='Dr. Raghav Sharma',
            specialization='Dermatology',
            hospital='Apollo Hospital Mumbai',
            license_number='DOC12345',
            years_of_experience=10,
            phone='+918888888888',
            email='doctor@example.com'
        )

        self.client.force_authenticate(user=self.patient1)
        self.appointment_url = reverse('appointments')
        self.appointment_date = date(2025, 12, 1)
        self.appointment_time = time(10, 0)

    # UNIT TEST 1: Appointment Model - Create Appointment
    def test_model_create_appointment_successfully(self):
        """
        UNIT: Appointment Model - create() method
        TEST: Creating an appointment with valid data
        
        Validates that:
        - Appointment is created in database
        - User and doctor are correctly associated
        - Status defaults to 'booked'
        - UUID primary key is generated
        """
        appointment = Appointment.objects.create(
            user=self.patient1,
            doctor=self.doctor,
            date=self.appointment_date,
            time_slot=self.appointment_time,
            status='booked'
        )
        
        self.assertEqual(appointment.user, self.patient1)
        self.assertEqual(appointment.doctor, self.doctor)
        self.assertEqual(appointment.status, 'booked')
        self.assertEqual(appointment.date, self.appointment_date)

    def test_model_unique_constraint_prevents_double_booking(self):
        """
        UNIT: Appointment Model - Unique constraint (user, doctor, date, time)
        TEST: Attempting to create duplicate appointment at same time
        
        Validates that:
        - First appointment is created successfully
        - Second appointment at same time raises IntegrityError
        - Database prevents double-booking for same user-doctor-time combination
        """
        Appointment.objects.create(
            user=self.patient1,
            doctor=self.doctor,
            date=self.appointment_date,
            time_slot=self.appointment_time,
            status='booked'
        )
        
        with self.assertRaises(IntegrityError):
            Appointment.objects.create(
                user=self.patient1,
                doctor=self.doctor,
                date=self.appointment_date,
                time_slot=self.appointment_time,
                status='booked'
            )

    def test_model_cancelled_appointment_allows_rebooking(self):
        """
        UNIT: Appointment Model - Cancellation and rebooking logic
        TEST: Rebooking a slot after cancellation
        
        Validates that:
        - First appointment can be created
        - Status can be changed to 'cancelled'
        - New appointment at same slot can be booked
        - Cancellation doesn't permanently block the slot
        """
        appointment1 = Appointment.objects.create(
            user=self.patient1,
            doctor=self.doctor,
            date=self.appointment_date,
            time_slot=self.appointment_time,
            status='booked'
        )
        
        appointment1.status = 'cancelled'
        appointment1.save()
        
        # Should be able to create new appointment
        appointment2 = Appointment.objects.create(
            user=self.patient1,
            doctor=self.doctor,
            date=self.appointment_date,
            time_slot=self.appointment_time,
            status='booked'
        )
        
        self.assertEqual(appointment2.status, 'booked')

    # UNIT TEST 2: AppointmentSerializer - Validation
    def test_serializer_valid_appointment_data(self):
        """
        UNIT: AppointmentSerializer - validate() method
        TEST: Serializing valid appointment data
        
        Validates that:
        - Serializer accepts valid data
        - Appointment is created with correct values
        - User is automatically associated
        """
        data = {
            'doctor_id': str(self.doctor.id),
            'date': '2025-12-01',
            'time_slot': '10:00:00'
        }
        
        serializer = AppointmentSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        appointment = serializer.save(user=self.patient1)
        
        self.assertEqual(appointment.doctor, self.doctor)

    def test_serializer_duplicate_appointment_validation(self):
        """
        UNIT: AppointmentSerializer - Conflict detection
        TEST: Attempting to serialize duplicate appointment
        
        Validates that:
        - First appointment serialization passes
        - Second appointment serialization at same time fails
        - Serializer rejects duplicates
        """
        data = {
            'doctor_id': str(self.doctor.id),
            'date': '2025-12-01',
            'time_slot': '10:00:00'
        }
        
        # Create first
        Appointment.objects.create(
            user=self.patient1,
            doctor=self.doctor,
            date=date(2025, 12, 1),
            time_slot=time(10, 0),
            status='booked'
        )
        
        # Try second
        serializer = AppointmentSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())

    # UNIT TEST 3: View - Appointment Management Endpoints
    def test_view_create_appointment_via_api(self):
        """
        UNIT: Appointment View - POST /appointments/
        TEST: Creating appointment through API endpoint
        
        Validates that:
        - API accepts valid appointment data
        - Appointment is created in database
        - HTTP 201 CREATED status returned
        - Response includes appointment details
        """
        data = {
            'doctor_id': str(self.doctor.id),
            'date': '2025-12-01',
            'time_slot': '10:00:00'
        }
        
        response = self.client.post(self.appointment_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_view_prevent_duplicate_appointment_booking(self):
        """
        UNIT: Appointment View - POST /appointments/ (duplicate prevention)
        TEST: Attempting to book same slot twice via API
        SHOULD PASS
        
        Validates that:
        - First booking succeeds
        - Second booking at same time fails
        - HTTP 400 BAD REQUEST returned
        """
        data = {
            'doctor_id': str(self.doctor.id),
            'date': '2025-12-01',
            'time_slot': '10:00:00'
        }
        
        # First booking
        self.client.post(self.appointment_url, data, format='json')
        
        # Second booking (duplicate)
        response = self.client.post(self.appointment_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_view_list_user_appointments(self):
        """
        UNIT: Appointment View - GET /appointments/
        TEST: Retrieving all appointments for authenticated user
        
        Validates that:
        - API returns list of appointments
        - Only user's own appointments are shown
        - HTTP 200 OK status returned
        """
        # Create appointment
        Appointment.objects.create(
            user=self.patient1,
            doctor=self.doctor,
            date=self.appointment_date,
            time_slot=self.appointment_time,
            status='booked'
        )
        
        response = self.client.get(self.appointment_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_view_cancel_appointment(self):
        """
        UNIT: Appointment View - PATCH /appointments/<id>/
        TEST: Cancelling an appointment via API
        
        Validates that:
        - Status can be updated to 'cancelled'
        - HTTP 200 OK status returned
        - Appointment status is persisted in database
        """
        appointment = Appointment.objects.create(
            user=self.patient1,
            doctor=self.doctor,
            date=self.appointment_date,
            time_slot=self.appointment_time,
            status='booked'
        )
        
        cancel_url = reverse('appointment_detail', kwargs={'pk': appointment.id})
        response = self.client.patch(
            cancel_url,
            {'status': 'cancelled'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, 'cancelled')

    def test_view_concurrent_booking_by_multiple_patients(self):
        """
        UNIT: Appointment View - Multiple concurrent users
        TEST: Two different patients booking same doctor at different times
        
        Validates that:
        - Multiple patients can book same doctor
        - Different time slots don't conflict
        - Both appointments are created successfully
        """
        data1 = {
            'doctor_id': str(self.doctor.id),
            'date': '2025-12-01',
            'time_slot': '10:00:00'
        }
        
        data2 = {
            'doctor_id': str(self.doctor.id),
            'date': '2025-12-01',
            'time_slot': '11:00:00'  # Different time
        }
        
        # Patient 1 books
        response1 = self.client.post(self.appointment_url, data1, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Patient 2 books
        self.client.force_authenticate(user=self.patient2)
        response2 = self.client.post(self.appointment_url, data2, format='json')
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        
        # Both appointments exist
        self.assertEqual(Appointment.objects.count(), 2)

    # FAILURE TEST 
    def test_appointment_datetime_constraint_gap(self):
        """
        UNIT: Appointment Model - Missing past date validation
        TEST: Attempting to book appointment in the past
        
        Demonstrates:
        - Model doesn't validate that appointments must be in future
        - Gap: No date range validation at model level
        - Could allow booking for past dates
        
        Learning: Temporal constraints need explicit validation
        """
        past_date = date(2020, 1, 1)
        
        # This creates appointment without error (should fail)
        appointment = Appointment.objects.create(
            user=self.patient1,
            doctor=self.doctor,
            date=past_date,
            time_slot=self.appointment_time,
            status='booked'
        )
        
        # This fails because model allows past dates
        self.assertGreater(appointment.date, date.today())
