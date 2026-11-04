"""Nurture / re-engagement sequences -- the part agencies charge monthly for.

Pure logic: given a timestamp anchor, return the messages DUE. Sending is
done only through services/sms.py, which honestly returns False until
Twilio is configured. Nothing here fakes a send.

Sequences reverse-engineered (clean-room, from public marketing pages):
- new_lead: instant (<60s), +1h, +1d, +3d, +7d  -- speed-to-lead + persistence
- appointment_reminder: -24h, -2h
- post_service: review request at completion, rebook prompt at +21d
- reactivation: ceramic maintenance at +180d, seasonal decon after winter,
  maintenance detail nudge at +90d since last completed service
All SMS copy includes opt-out handling expectations (STOP) in DEPLOY.md.
"""
from datetime import datetime, timedelta
SHOP = "Clinton Auto Detailing, 715 Park Place, Clinton, IA"
BOOKING_URL = "https://clintondetail.com/book"

NEW_LEAD_STEPS = [
    (timedelta(seconds=0), "Hey {name}, thanks for reaching out to Clinton Auto Detailing! What year/make/model are we treating, and what are you hoping it looks like when it's done?"),
    (timedelta(hours=1), "Still happy to get you a slot this week, {name}. Reply with your vehicle and I'll lock a bay time at 715 Park Place."),
    (timedelta(days=1), "Quick follow-up -- bay times fill fast. You can grab one here: " + BOOKING_URL),
    (timedelta(days=3), "Want me to hold a tentative slot for your {vehicle}? No deposit, just reply YES and I'll pencil it in."),
    (timedelta(days=7), "Last nudge from us, {name}. If timing's off, reply LATER and we'll check back next season instead of bugging you."),
]
REMINDER_STEPS = [
    (timedelta(hours=-24), "Reminder: your {vehicle} is booked tomorrow at {time} at 715 Park Place. Reply C to confirm or R to reschedule."),
    (timedelta(hours=-2), "See you in about 2 hours for your {vehicle}. Drop-off is 715 Park Place, Clinton."),
]
REACTIVATION_RULES = [
    ("Ceramic Coating", timedelta(days=180), "It's been about 6 months since your ceramic coating. A maintenance wash/decon keeps it performing -- want a slot?"),
    ("Multi-Stage Paint Correction & Ceramic", timedelta(days=180), "It's been about 6 months since your correction + ceramic. A maintenance service keeps the coating performing -- want a slot?"),
    ("Standard Detail", timedelta(days=90), "It's been about 3 months since your last detail. Want us to get your {vehicle} back on the calendar?"),
    ("*", timedelta(days=120), "Seasonal check-in: road salt and winter grime are rough on paint. A decontamination detail protects it -- interested?"),
]

def due_new_lead_messages(lead_created_at: datetime, now: datetime, name: str = "there", vehicle: str = "vehicle"):
    due = []
    for offset, tpl in NEW_LEAD_STEPS:
        if now >= lead_created_at + offset:
            due.append(tpl.format(name=name, vehicle=vehicle))
    return due

def due_reactivation(last_service_type: str, last_completed_at: datetime, now: datetime, vehicle: str = "vehicle"):
    for svc, delay, tpl in REACTIVATION_RULES:
        if (svc == "*" or svc == last_service_type) and now >= last_completed_at + delay:
            return tpl.format(vehicle=vehicle)
    return None
