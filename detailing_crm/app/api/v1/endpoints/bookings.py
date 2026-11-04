"""Frictionless booking: instant calendar hold, NO deposit gate.

Owner decision 2026-11-04 supersedes the earlier Stripe/USDC draft.
Uses dynamic vehicle-size pricing (quote only) and duration+buffer
overlap checking (services/calendar_logic.py).
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import SHOP_ADDRESS
from app.models.appointment import AppointmentModel
from app.models.client import ClientModel
from app.models.vehicle import VehicleModel
from app.schemas.booking import BookingCreateRequest, QuoteRequest
from app.services.sms import send_instant_sms
from app.services.pricing import quote as price_quote
from app.services.calendar_logic import is_slot_available

router = APIRouter(prefix="/bookings", tags=["Bookings"])

@router.post("/quote")
async def get_quote(payload: QuoteRequest):
    return price_quote(payload.service_type, payload.vehicle_size)

@router.get("/availability")
async def availability(date: str, service_type: str = "Standard Detail", db: AsyncSession = Depends(get_db)):
    q = price_quote(service_type)
    day = datetime.fromisoformat(date)
    result = await db.execute(select(AppointmentModel).where(AppointmentModel.status.in_(["scheduled", "in_bay"])))
    existing = [(a.scheduled_time, a.estimated_duration_hours) for a in result.scalars().all() if a.scheduled_time.date() == day.date()]
    slots = []
    for hour in (8, 9, 10, 11, 12, 13, 14, 15):
        start = day.replace(hour=hour, minute=0, second=0, microsecond=0)
        slots.append({"start": start.isoformat(), "available": is_slot_available(existing, start, q["estimated_duration_hours"])})
    return {"date": date, "service_type": service_type, "slots": slots}

@router.post("/create-appointment", status_code=201)
async def create_appointment(payload: BookingCreateRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ClientModel).where(ClientModel.phone == payload.phone))
    client = result.scalar_one_or_none()
    if client is None:
        client = ClientModel(name=payload.name, phone=payload.phone, email=payload.email)
        db.add(client); await db.flush()
    result = await db.execute(select(VehicleModel).where(
        VehicleModel.client_id == client.id, VehicleModel.year == payload.vehicle_year,
        VehicleModel.make == payload.vehicle_make, VehicleModel.model == payload.vehicle_model))
    vehicle = result.scalar_one_or_none()
    if vehicle is None:
        vehicle = VehicleModel(client_id=client.id, year=payload.vehicle_year, make=payload.vehicle_make,
                               model=payload.vehicle_model, paint_color=payload.paint_color, vin=payload.vin)
        db.add(vehicle); await db.flush()
    q = price_quote(payload.service_type, payload.vehicle_size)
    result = await db.execute(select(AppointmentModel).where(AppointmentModel.status.in_(["scheduled", "in_bay"])))
    existing = [(a.scheduled_time, a.estimated_duration_hours) for a in result.scalars().all()]
    if not is_slot_available(existing, payload.scheduled_time, q["estimated_duration_hours"]):
        raise HTTPException(status_code=409, detail="That bay time overlaps an existing job. Please pick another slot.")
    appointment = AppointmentModel(vehicle_id=vehicle.id, service_type=payload.service_type,
        scheduled_time=payload.scheduled_time, estimated_duration_hours=q["estimated_duration_hours"],
        total_price=q["estimated_price"], deposit_paid=False, status="scheduled",
        source=payload.source, notes=payload.notes)
    db.add(appointment); await db.commit(); await db.refresh(appointment)
    sms_sent = await send_instant_sms(payload.phone,
        f"Hey {payload.name}, your bay slot at {SHOP_ADDRESS} is locked in for "
        f"{payload.scheduled_time.strftime('%B %d at %I:%M %p')} for your "
        f"{payload.vehicle_year} {payload.vehicle_make} {payload.vehicle_model}. We'll see you then! Reply STOP to opt out.")
    return {"status": "confirmed", "appointment_id": appointment.id, "total_price": q["estimated_price"],
            "price_note": q["note"], "deposit_required": False, "sms_sent": sms_sent, "bay_location": SHOP_ADDRESS}

@router.post("/{appointment_id}/complete")
async def complete_appointment(appointment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AppointmentModel).where(AppointmentModel.id == appointment_id))
    appt = result.scalar_one_or_none()
    if appt is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appt.status = "completed"; appt.completed_at = datetime.utcnow()
    # Review request fires at completion -- the highest-converting moment, per every competitor teardown.
    vehicle = await db.get(VehicleModel, appt.vehicle_id)
    client = await db.get(ClientModel, vehicle.client_id) if vehicle else None
    sms_sent = False
    if client:
        sms_sent = await send_instant_sms(client.phone,
            "Thanks for trusting Clinton Auto Detailing! If we earned it, a 5-star Google review helps a ton. Reply here if anything needs a touch-up.")
        appt.review_requested = sms_sent
    await db.commit()
    return {"status": "completed", "appointment_id": appt.id, "review_sms_sent": sms_sent}
