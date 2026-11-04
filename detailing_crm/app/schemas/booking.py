from datetime import datetime
from pydantic import BaseModel, Field

class BookingCreateRequest(BaseModel):
    name: str = Field(..., description="Client full name")
    phone: str = Field(..., description="Client phone number")
    email: str | None = Field(None, description="Client email")
    vehicle_year: int = Field(..., description="Vehicle year")
    vehicle_make: str = Field(..., description="Vehicle make (e.g. Ford)")
    vehicle_model: str = Field(..., description="Vehicle model (e.g. Mustang)")
    vehicle_size: str = Field("sedan", description="coupe|sedan|small_suv|full_suv|truck|3row|van")
    paint_color: str | None = None
    vin: str | None = None
    service_type: str = Field(..., description="Requested detailing service")
    scheduled_time: datetime = Field(..., description="Desired appointment timestamp")
    source: str | None = Field("website", description="website|meta_ad|sms|missed_call|google")
    notes: str | None = None

class QuoteRequest(BaseModel):
    service_type: str
    vehicle_size: str = "sedan"
