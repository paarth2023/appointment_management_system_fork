import json
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from google import genai
from google.genai import types

client = genai.Client(api_key=settings.GEMINI_API_KEY)
MODEL_NAME = "gemini-2.5-flash"


def format_response_with_llm(action, data, user_message):
    """
    Use Gemini to format the action result into a natural, user-friendly response.
    Returns a formatted message string in markdown format.
    """

    # SAFE serialization (UUID, datetime, Decimal, etc.)
    safe_data = json.dumps(data, indent=2, cls=DjangoJSONEncoder)

    formatting_prompt = f"""You are a friendly booking assistant. Format the following data into a natural, conversational response for the user.

USER'S MESSAGE: {user_message}

ACTION PERFORMED: {action}

DATA RETURNED:
{safe_data}

FORMATTING GUIDELINES:
1. Be conversational and friendly
2. Use markdown formatting for better readability
3. For services: Present them in a clear list with key details
4. For availability: Show time slots in an organized way
5. For bookings: Confirm the booking details clearly
6. For payments: Provide payment instructions and next steps
7. Use emojis sparingly but effectively (✅, 📅, ⏰, 💰, etc.)
8. Keep it concise but informative
9. Always end with a helpful next step or question

RESPONSE (markdown formatted):"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=formatting_prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=1000,
            ),
        )

        return response.text.strip()

    except Exception:
        return format_response_fallback(action, data)


def format_response_fallback(action, data):
    """Fallback formatting if LLM is unavailable"""

    if action == "list_services":
        services = data if isinstance(data, list) else []
        if not services:
            return "No services are currently available."

        msg = "**Available Services:**\n\n"
        for svc in services:
            msg += f"• **{svc.get('name', 'Unnamed Service')}**\n"
            if svc.get("description"):
                msg += f"  _{svc['description']}_\n"
            if svc.get("price"):
                msg += f"  💰 Price: ₹{svc['price']}\n"
            if svc.get("duration_minutes"):
                msg += f"  ⏱️ Duration: {svc['duration_minutes']} minutes\n"
            msg += "\n"
        return msg

    elif action == "check_availability":
        slots = data if isinstance(data, list) else []
        if not slots:
            return "No available slots found for the selected date."

        msg = "**Available Time Slots:**\n\n"
        for slot in slots:
            start_time = slot.get("start", "")
            if isinstance(start_time, str) and "T" in start_time:
                time_str = start_time.split("T")[1][:5]
                msg += f"• {time_str} - Available\n"
            else:
                msg += f"• Slot ID: {slot.get('id')} - Available\n"

        msg += "\nTo book a slot, please tell me which time works for you."
        return msg

    elif action == "create_booking":
        return (
            "✅ **Booking Created Successfully!**\n\n"
            f"Booking ID: `{data.get('id', 'N/A')}`\n\n"
            "Your appointment has been confirmed."
        )

    elif action == "create_payment_order":
        return (
            "💰 **Payment Order Created**\n\n"
            f"Amount: ₹{data.get('amount', 'N/A')}\n\n"
            "Please proceed with the payment to confirm your booking."
        )

    # SAFE fallback serialization
    return json.dumps(data, indent=2, cls=DjangoJSONEncoder)
