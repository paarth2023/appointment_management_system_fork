from typing import Dict

AGENT_ACTIONS: Dict[str, Dict] = {
    "list_services": {
        "description": "List published services",
        "params": {},
        "required": [],
    },

    "check_availability": {
        "description": "Check available slots for a service on a date",
        "params": {
            "service_id": "INTEGER Service ID",
            "date": "YYYY-MM-DD",
        },
        "required": ["service_id", "date"],
    },

    "create_booking": {
        "description": "Create a booking for a slot",
        "params": {
            "slot_id": "INTEGER Slot ID",
            "answers": "object",
        },
        "required": ["slot_id"],
    },

    "create_payment_order": {
        "description": "Create Razorpay order",
        "params": {
            "booking_id": "UUID",
        },
        "required": ["booking_id"],
    },
}
