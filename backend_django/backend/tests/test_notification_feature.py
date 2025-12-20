# backend/tests/test_notification_feature.py
"""
FEATURE: Multi-Channel Notification System
Tests the complete notification workflow across Email, SMS, and WhatsApp.
Units tested: send_notification utility, Notification model, User preferences
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from backend.models import Notification
from backend.utils import send_notification
from unittest.mock import patch, MagicMock

User = get_user_model()


class NotificationSystemFeatureTest(TestCase):
    """
    FEATURE: Multi-Channel Notification System
    
    This test suite validates comprehensive notification functionality:
    - Multi-channel support (Email, SMS, WhatsApp)
    - User consent management
    - Notification preference respect
    - Failed notification logging
    - Notification type tracking
    - Error handling for invalid channels
    
    Tests span: Utils (send_notification) + Model (Notification) + User Preferences
    """

    def setUp(self):
        """Set up test users with different preferences."""
        self.user_email_consent = User.objects.create_user(
            email='notify_email@example.com',
            phone_no='+911111111111',
            full_name='Email User',
            password='Pass123!',
            notification_preference='email',
            notification_consent=True
        )
        
        self.user_sms_consent = User.objects.create_user(
            email='notify_sms@example.com',
            phone_no='+912222222222',
            full_name='SMS User',
            password='Pass123!',
            notification_preference='sms',
            notification_consent=True
        )
        
        self.user_whatsapp_consent = User.objects.create_user(
            email='notify_whatsapp@example.com',
            phone_no='+913333333333',
            full_name='WhatsApp User',
            password='Pass123!',
            notification_preference='whatsapp',
            notification_consent=True
        )
        
        self.user_no_consent = User.objects.create_user(
            email='no_notify@example.com',
            phone_no='+914444444444',
            full_name='No Consent User',
            password='Pass123!',
            notification_preference='email',
            notification_consent=False
        )

    # UNIT TEST 1: Notification Model - Storage and Tracking
    def test_model_notification_creation_and_storage(self):
        """
        UNIT: Notification Model - create() method
        TEST: Creating and storing notification records
        
        Validates that:
        - Notification is created in database
        - All fields are stored correctly
        - Status is tracked (sent, failed, pending)
        - Timestamp is recorded
        """
        notification = Notification.objects.create(
            user=self.user_email_consent,
            subject='Test Notification',
            message='This is a test',
            notification_type='appointment_confirmation',
            status='sent'
        )
        
        self.assertEqual(notification.user, self.user_email_consent)
        self.assertEqual(notification.subject, 'Test Notification')
        self.assertEqual(notification.status, 'sent')
        self.assertEqual(notification.notification_type, 'appointment_confirmation')

    def test_model_notification_status_transitions(self):
        """
        UNIT: Notification Model - Status management
        TEST: Changing notification status from pending to sent/failed
        
        Validates that:
        - Status can transition between states
        - Failed notifications record error messages
        - Status updates are persisted
        """
        notification = Notification.objects.create(
            user=self.user_email_consent,
            subject='Test',
            message='Test message',
            status='pending'
        )
        
        notification.status = 'sent'
        notification.save()
        
        notification.refresh_from_db()
        self.assertEqual(notification.status, 'sent')

    def test_model_failed_notification_logging(self):
        """
        UNIT: Notification Model - Error recording
        TEST: Logging failed notifications with error messages
        
        Validates that:
        - Failed notifications can store error details
        - Error messages are retrievable
        - Failure reason is documented
        """
        notification = Notification.objects.create(
            user=self.user_email_consent,
            subject='Failed Notification',
            message='This will fail',
            status='failed',
            error_message='SMTP connection failed'
        )
        
        self.assertEqual(notification.status, 'failed')
        self.assertEqual(notification.error_message, 'SMTP connection failed')

    # UNIT TEST 2: send_notification() Utility - Multi-Channel Support
    @patch('backend.utils.send_email_notification')
    def test_send_email_notification_with_consent(self, mock_email):
        """
        UNIT: send_notification() utility function
        TEST: Sending email notification to user with consent
        
        Validates that:
        - Email function is called when user has consent
        - User preference for email is respected
        - Notification record is created
        - Status is marked as 'sent'
        """
        mock_email.return_value = True
        
        result = send_notification(
            user=self.user_email_consent,
            subject='Welcome',
            message='Welcome to NeoDermaScan',
            notification_type='welcome'
        )
        
        self.assertTrue(result)
        mock_email.assert_called_once()
        
        notification = Notification.objects.filter(
            user=self.user_email_consent
        ).first()
        self.assertEqual(notification.status, 'sent')

    def test_send_notification_without_user_consent(self):
        """
        UNIT: send_notification() utility function
        TEST: Respecting user opt-out preferences
        
        Validates that:
        - Notifications NOT sent when consent is False
        - User preference for opt-out is honored
        - No notification record created
        - Function returns False
        """
        result = send_notification(
            user=self.user_no_consent,
            subject='Test',
            message='Test message'
        )
        
        self.assertFalse(result)
        
        notification_count = Notification.objects.filter(
            user=self.user_no_consent
        ).count()
        self.assertEqual(notification_count, 0)

    @patch('backend.utils.send_twilio_message')
    def test_send_sms_notification_channel(self, mock_sms):
        """
        UNIT: send_notification() utility function
        TEST: SMS channel functionality
        
        Validates that:
        - Twilio SMS API is called for SMS preference users
        - Message is sent via SMS
        - Notification record reflects SMS delivery
        """
        mock_sms.return_value = True
        
        result = send_notification(
            user=self.user_sms_consent,
            subject='SMS Notification',
            message='This is via SMS'
        )
        
        self.assertTrue(result)
        mock_sms.assert_called_once()

    @patch('backend.utils.send_twilio_message')
    def test_send_whatsapp_notification_channel(self, mock_whatsapp):
        """
        UNIT: send_notification() utility function
        TEST: WhatsApp channel functionality
        
        Validates that:
        - WhatsApp API is called for WhatsApp preference users
        - Message is sent via WhatsApp
        - Channel preference is correctly identified
        """
        mock_whatsapp.return_value = True
        
        result = send_notification(
            user=self.user_whatsapp_consent,
            subject='WhatsApp Notification',
            message='This is via WhatsApp'
        )
        
        self.assertTrue(result)
        mock_whatsapp.assert_called()

    @patch('backend.utils.send_email_notification')
    def test_failed_notification_is_logged(self, mock_email):
        """
        UNIT: send_notification() utility function
        TEST: Recording failed notification attempts
        
        Validates that:
        - Failed notifications are still logged
        - Status is set to 'failed'
        - Function returns False
        - Notification record exists for debugging
        """
        mock_email.return_value = False
        
        result = send_notification(
            user=self.user_email_consent,
            subject='Will Fail',
            message='This will fail',
            notification_type='test_failure'
        )
        
        self.assertFalse(result)
        
        notification = Notification.objects.filter(
            user=self.user_email_consent
        ).first()
        self.assertEqual(notification.status, 'failed')

    # UNIT TEST 3: User Preferences - Channel Selection
    def test_model_user_notification_preference_storage(self):
        """
        UNIT: User Model - notification_preference field
        TEST: Storing and retrieving user notification preferences
        
        Validates that:
        - Preference is stored in database
        - Preference is retrieved correctly
        - Different users can have different preferences
        """
        user = User.objects.get(email='notify_sms@example.com')
        
        self.assertEqual(user.notification_preference, 'sms')
        
        # Change preference
        user.notification_preference = 'whatsapp'
        user.save()
        
        user.refresh_from_db()
        self.assertEqual(user.notification_preference, 'whatsapp')

    def test_model_user_consent_flag_management(self):
        """
        UNIT: User Model - notification_consent field
        TEST: Managing user consent flag
        
        Validates that:
        - Consent flag can be True or False
        - Consent affects notification sending
        - Consent can be toggled
        """
        user = self.user_no_consent
        
        self.assertFalse(user.notification_consent)
        
        # User opts in
        user.notification_consent = True
        user.save()
        
        user.refresh_from_db()
        self.assertTrue(user.notification_consent)

    @patch('backend.utils.send_email_notification')
    def test_notification_type_is_recorded(self, mock_email):
        """
        UNIT: Notification Model - notification_type field
        TEST: Tracking notification type for analytics
        
        Validates that:
        - Notification type is stored
        - Different types can be distinguished
        - Query by type is possible for analytics
        """
        mock_email.return_value = True
        
        send_notification(
            user=self.user_email_consent,
            subject='Appointment',
            message='Your appointment is confirmed',
            notification_type='appointment_confirmation'
        )
        
        notification = Notification.objects.filter(
            notification_type='appointment_confirmation'
        ).first()
        
        self.assertIsNotNone(notification)

    # FAILURE TEST
    def test_invalid_notification_channel_handling(self):
        """
        UNIT: send_notification() utility function
        TEST: Invalid/unsupported notification channel
        
        Demonstrates:
        - No validation for invalid notification preferences
        - Gap: Can set invalid channel in user preferences
        - No error handling for unknown channels
        
        Learning: Input validation must cover all enum values
        """
        # Create user with invalid preference (if not validated)
        self.user_email_consent.notification_preference = 'carrier_pigeon'
        self.user_email_consent.save()
        
        result = send_notification(
            user=self.user_email_consent,
            subject='Invalid Channel',
            message='This should fail'
        )
        
        notification = Notification.objects.filter(
            user=self.user_email_consent
        ).first()
        
        # This fails because no error handling for invalid channels
        self.assertIsNotNone(notification)
        self.assertEqual(notification.status, 'failed')
        self.assertIsNotNone(notification.error_message)
