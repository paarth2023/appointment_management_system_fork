from dataclasses import dataclass

@dataclass
class BookingCreatedEvent:
    booking_id: str

@dataclass
class BookingCancelledEvent:
    booking_id: str

@dataclass
class PaymentCompletedEvent:
    booking_id: str
