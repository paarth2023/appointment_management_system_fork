import os
from math import asin, cos, radians, sin, sqrt
from django.utils import timezone

import requests
from django.conf import settings
from django.core.mail import send_mail
from django.core.files.storage import default_storage

# Twilio
TWILIO_ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN
TWILIO_PHONE_NUMBER = settings.TWILIO_PHONE_NUMBER
TWILIO_WHATSAPP_NUMBER = settings.TWILIO_WHATSAPP_NUMBER

GOOGLE_API_KEY = getattr(settings, "GOOGLE_MAPS_API_KEY", None)





def get_nearby_hospitals(lat, lon, radius=5000):
    """Fetch nearby hospitals using Google Places API"""
    if not GOOGLE_API_KEY:
        return []

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lon}",
        "radius": radius,
        "type": "hospital",
        "key": GOOGLE_API_KEY,
    }
    try:
        resp = requests.get(url, params=params, timeout=10).json()
        return resp.get("results", [])
    except Exception as e:
        # print(f"Google Places API error: {e}")
        return []


def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    R = 6371  # Earth's radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    return 2 * R * asin(sqrt(a))


def upload_file(file, user_id):
    """
    Upload file to Local Storage
    Returns: (storage_path, public_url) or (None, None) if failed
    """
    try:
        # Generate unique filename
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        original_name = file.name
        unique_filename = f"uploads/{user_id}/{timestamp}_{original_name}"

        # Save locally
        path = default_storage.save(unique_filename, file)
        
        # Get public URL
        public_url = settings.MEDIA_URL + path

        return path, public_url

    except Exception as e:
        # print(f"Upload error: {e}")
        return None, None


def send_email_notification(subject, message, recipient):
    """
    Send email notification using Django's built-in email system
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[recipient],
            fail_silently=False,
        )
        return True
    except Exception as e:
        # print(f"Email sending failed: {e}")
        return False


def send_twilio_message(phone, message, whatsapp=False):
    """
    Send SMS or WhatsApp notification using Twilio API.

    Args:
        phone (str): Recipient phone number
        message (str): Message body
        whatsapp (bool): If True, send via WhatsApp. Otherwise, SMS.
    Returns:
        bool: True if sent successfully, False otherwise
    """

    # Determine the Twilio "from" number
    from_number = TWILIO_WHATSAPP_NUMBER if whatsapp else TWILIO_PHONE_NUMBER

    # Check required credentials
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, from_number]):
        # print("Twilio credentials not configured")
        return False

    try:
        from twilio.rest import Client

        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        # Format phone number for WhatsApp
        if whatsapp and not str(phone).startswith("whatsapp:"):
            phone = f"whatsapp:{phone}"

        msg = client.messages.create(body=message, from_=from_number, to=str(phone))
        channel = "WhatsApp" if whatsapp else "SMS"
        # print(f"{channel} sent successfully: {msg.sid}")
        return True

    except Exception as e:
        channel = "WhatsApp" if whatsapp else "SMS"
        # print(f"{channel} sending failed: {e}")
        return False


def send_notification(
    user, subject, message, notification_type="appointment_confirmation"
):
    """
    Unified notification sender that respects user preferences
    Creates Notification record and sends via preferred channel
    """
    from .models import Notification

    # Check if user has given consent
    if not user.notification_consent:
        # print(f"User {user.email} has not given notification consent")
        return False

    # Determine channel
    channel = user.notification_preference
    success = False
    error_message = None

    # Send notification based on preference
    try:
        if channel == "email":
            success = send_email_notification(subject, message, user.email)
        elif channel == "sms":
            success = send_twilio_message(user.phone_no, message)
        elif channel == "whatsapp":
            success = send_twilio_message(user.phone_no, message, whatsapp=True)
        else:
            error_message = f"Unknown channel: {channel}"
    except Exception as e:
        error_message = str(e)

    # Create notification record
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        channel=channel,
        subject=subject,
        message=message,
        status="sent" if success else "failed",
        sent_at=timezone.now() if success else None,
        error_message=error_message,
    )

    return success
