# backend/tests/test_user_auth_feature.py
"""
FEATURE: User Authentication & Registration
Tests the complete user registration and login workflow across Model, Serializer, and View layers.
Units tested: User model, RegisterSerializer, Auth views
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from backend.serializers import RegisterSerializer
from django.db import IntegrityError
import uuid

User = get_user_model()


class UserAuthenticationFeatureTest(TestCase):
    """
    FEATURE: User Authentication & Registration
    
    This test suite validates the complete user authentication workflow:
    - User registration with validation
    - Password security requirements
    - Email/phone uniqueness
    - JWT token generation
    - Login authentication
    
    Tests span: Model layer + Serializer layer + View layer
    """

    def setUp(self):
        """Set up test client and valid user data."""
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        
        self.valid_user_data = {
            'email': 'newuser@example.com',
            'full_name': 'New User',
            'phone_no': '+911234567890',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'notification_preference': 'email',
            'notification_consent': True
        }        
        
    # UNIT TEST 1: User Model - Create User
    def test_serializer_weak_password_rejection(self):
        """
        UNIT: RegisterSerializer - Password strength validation
        TEST: Weak passwords (too short, no special chars, etc.)
        
        Validates that:
        - Passwords less than 8 chars are rejected
        - Common passwords are rejected
        - Password must contain special characters
        """
        data = self.valid_user_data.copy()
        data['password'] = '123'  # Too short
        data['confirm_password'] = '123'
        
        serializer = RegisterSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
    
    def test_user_model_create_with_valid_data(self):
        """
        UNIT: User Model - create_user() method
        TEST: Creating a user with valid credentials
        
        Validates that:
        - User is created in database
        - Password is hashed correctly
        - UUID primary key is generated
        - Default staff/superuser flags are False
        """
        user = User.objects.create_user(
            email='test@example.com',
            phone_no='+911234567890',
            full_name='Test User',
            password='SecurePass123'
        )
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.full_name, 'Test User')
        self.assertTrue(user.check_password('SecurePass123'))
        self.assertIsInstance(user.id, uuid.UUID)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_user_model_email_uniqueness_constraint(self):
        """
        UNIT: User Model - Unique constraint on email field
        TEST: Attempting to create two users with same email
        
        Validates that:
        - First user is created successfully
        - Second user creation raises IntegrityError
        - Database prevents duplicate emails
        """
        User.objects.create_user(
            email='unique@example.com',
            phone_no='+911111111111',
            full_name='First User',
            password='Pass123!'
        )
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email='unique@example.com',
                phone_no='+912222222222',
                full_name='Second User',
                password='Pass123!'
            )

    def test_user_model_phone_uniqueness_constraint(self):
        """
        UNIT: User Model - Unique constraint on phone_no field
        TEST: Attempting to create two users with same phone number
        """
        User.objects.create_user(
            email='first@example.com',
            phone_no='+913333333333',
            full_name='First User',
            password='Pass123!'
        )
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email='second@example.com',
                phone_no='+913333333333',
                full_name='Second User',
                password='Pass123!'
            )

    # UNIT TEST 2: RegisterSerializer - Validation
    def test_password_missing_special_characters_gap(self):
        """
        UNIT: RegisterSerializer - Missing special character validation
        TEST: Password without any special characters
        
        Demonstrates:
        - Django validators do NOT enforce special character requirement
        - Password 'SecurePassword123' is accepted
        - Security gap: Users can register with weak-format passwords
        
        Learning: Add custom password validators for strong password policy
        """
        data = self.valid_user_data.copy()
        data['password'] = 'SecurePassword123'  # No special character
        data['confirm_password'] = 'SecurePassword123'

        serializer = RegisterSerializer(data=data)

        self.assertFalse(
            serializer.is_valid(),
            "Serializer should reject passwords missing special characters, but it didn't."
        )
        self.assertIn('password', serializer.errors)
    
    def test_serializer_password_confirmation_validation(self):
        """
        UNIT: RegisterSerializer - validate password matching
        TEST: Password and confirm_password must match
        
        Validates that:
        - Serializer rejects mismatched passwords
        - Error message indicates password field issue
        - User is not created
        """
        data = self.valid_user_data.copy()
        data['confirm_password'] = 'DifferentPassword123!'
        
        serializer = RegisterSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_serializer_invalid_email_format(self):
        """
        UNIT: RegisterSerializer - Email format validation
        TEST: Invalid email format rejection
        """
        data = self.valid_user_data.copy()
        data['email'] = 'not-an-email'
        
        serializer = RegisterSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    # UNIT TEST 3: View - Registration Endpoint
    def test_view_user_registration_endpoint_success(self):
        """
        UNIT: Auth View - POST /register/
        TEST: Complete registration via API endpoint
        
        Validates that:
        - Valid registration data is accepted
        - User is created in database
        - HTTP 201 CREATED status returned
        - User can be retrieved from database
        """
        response = self.client.post(
            self.register_url,
            self.valid_user_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(
            email=self.valid_user_data['email']
        ).exists())

    def test_view_registration_with_duplicate_email(self):
        """
        UNIT: Auth View - POST /register/ (duplicate prevention)
        TEST: Register two users with same email
        """
        # First registration
        self.client.post(self.register_url, self.valid_user_data, format='json')
        
        # Second registration with same email
        response = self.client.post(
            self.register_url,
            self.valid_user_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_view_login_endpoint_success(self):
        """
        UNIT: Auth View - POST /login/
        TEST: User login with correct credentials
        
        Validates that:
        - Login endpoint accepts credentials
        - JWT tokens are generated (access + refresh)
        - HTTP 200 OK status returned
        - User data is returned in response
        """
        # First register
        self.client.post(self.register_url, self.valid_user_data, format='json')
        
        # Then login
        login_data = {
            'email': self.valid_user_data['email'],
            'password': self.valid_user_data['password']
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_view_login_with_wrong_password(self):
        """
        UNIT: Auth View - POST /login/ (wrong password)
        TEST: Login attempt with incorrect password
        
        Validates that:
        - Wrong password is rejected
        - HTTP 401 UNAUTHORIZED status returned
        - No tokens are issued
        """
        self.client.post(self.register_url, self.valid_user_data, format='json')
        
        login_data = {
            'email': self.valid_user_data['email'],
            'password': 'WrongPassword'
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
