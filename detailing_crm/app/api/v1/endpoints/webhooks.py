"""Inbound capture: Meta Lead Ads, Twilio SMS inbound, missed-call text-back.

Speed-to-lead target: respond in <60 seconds. The webhook itself returns
immediately after logging; the qualification SMS is the first nurture step.
STOP / opt-out: an inbound STOP marks the lead opted out and no further
nurture is sent to that number.
"""
from fastapi import APIRouter, Depends, Form, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.lead import LeadModel
from app.schemas.lead import InboundLeadPayload
from app.services.sms import send_instant_sms

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])
QUALIFY_MSG = "Hey! Saw you're looking for professional detailing in Clinton. What year/make/model are we treating?"
MISSED_CALL_MSG = "Sorry we missed your call at Clinton Auto Detailing! We're likely mid-detail. Reply here or book instantly: https://clintondetail.com/book"

async def _log_lead(db, phone, source, message=None, name=None):
    lead = LeadModel(phone=phone, source=source, raw_payload=f"Name: {name} | Message: {message}", status="new", name=name)
    db.add(lead); await db.commit(); await db.refresh(lead); return lead

@router.post("/lead-capture", status_code=status.HTTP_201_CREATED)
async def capture_inbound_lead(payload: InboundLeadPayload, db: AsyncSession = Depends(get_db)):
    lead = await _log_lead(db, payload.phone, payload.source, payload.message, payload.name)
    sms_sent = await send_instant_sms(payload.phone, QUALIFY_MSG)
    return {"status": "success", "lead_id": lead.id, "message": "Lead ingested and qualification sequence triggered.", "sms_sent": sms_sent}

@router.post("/missed-call", status_code=status.HTTP_201_CREATED)
async def missed_call(payload: InboundLeadPayload, db: AsyncSession = Depends(get_db)):
    lead = await _log_lead(db, payload.phone, "missed_call", "Missed call", payload.name)
    sms_sent = await send_instant_sms(payload.phone, MISSED_CALL_MSG)
    return {"status": "success", "lead_id": lead.id, "action": "missed_call_text_back", "sms_sent": sms_sent}

@router.post("/sms-inbound")
async def sms_inbound(From: str = Form(...), Body: str = Form(""), db: AsyncSession = Depends(get_db)):
    """Twilio inbound SMS webhook (form-encoded). Handles STOP opt-out."""
    body = (Body or "").strip()
    if body.upper() in ("STOP", "STOPALL", "UNSUBSCRIBE", "CANCEL", "END", "QUIT"):
        result = await db.execute(select(LeadModel).where(LeadModel.phone == From))
        for lead in result.scalars().all():
            lead.opt_out = True
        await db.commit()
        return {"status": "opted_out", "phone": From}
    lead = await _log_lead(db, From, "sms_inbound", body)
    return {"status": "success", "lead_id": lead.id}
