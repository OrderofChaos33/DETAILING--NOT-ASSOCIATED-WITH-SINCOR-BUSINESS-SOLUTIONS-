# Architecture — Clinton Auto Detailing, clintondetail.com

Separate business, separate repo. Not associated with SINCOR Business Solutions.

```
 Lead sources                          This repo
 ─────────────                         ─────────────────────────────────────
 Meta Lead Ads ──webhook──┐
 Website form (frontend/)─┼─> FastAPI ──> PostgreSQL (clients / vehicles /
 Google Business msgs ────┤   (detailing_crm)   leads / appointments)
 Missed call (Twilio) ────┤        │
 Inbound SMS (Twilio) ────┘        ├─> services/pricing.py   (size x service quote)
                                   ├─> services/calendar_logic.py (duration+buffer, bay capacity)
                                   ├─> services/nurture.py   (new-lead, reminder, review, reactivation — pure logic)
                                   └─> services/sms.py       (Twilio REST when configured, else honest False)
```

## Flow: lead → booked calendar → completed service

1. Capture (<60s): any source posts to `/api/v1/webhooks/lead-capture`
   (or `/missed-call`, `/sms-inbound`). Lead is logged first, qualification
   SMS second — logging never waits on the text.
2. Quote: `/api/v1/bookings/quote` prices service × vehicle size instantly,
   with the honesty note that final price is confirmed after seeing condition.
3. Book: `/api/v1/bookings/create-appointment` finds/creates client by phone,
   registers/reuses the vehicle asset, checks duration+buffer overlap,
   creates a **confirmed hold — no deposit**, fires the confirmation SMS
   ("locked in for [date] … 715 Park Place").
4. Remind: nurture reminder steps at −24h / −2h (scheduler wiring is the
   deploy step in DEPLOY.md; the message logic is built and tested).
5. Complete: `POST /api/v1/bookings/{id}/complete` stamps completion and
   fires the review request at the happiest moment.
6. Reactivate: nurture rules keyed to last service (90d detail, 180d ceramic,
   seasonal decon) bring the calendar back-fill from past customers —
   the cheapest leads a shop owns.

## Data model (vehicle-first)

- clients: phone is the unique key; one client → many vehicles.
- vehicles: year/make/model, paint color, VIN, notes; appointments hang off
  the vehicle, so service history is per-asset, not per-person.
- leads: source, status (new/qualified/booked/dead), service interest,
  opt_out (STOP), raw payload for audit.
- appointments: service, start, duration hours, buffer minutes, quoted price,
  status (scheduled/in_bay/completed/canceled), source, completed_at,
  review_requested. `deposit_paid` stays False by design (no-deposit model).

## Security (from the owner's production paste, kept)

TrustedHost (clintondetail.com only), CORS whitelist, docs disabled in
production, HSTS / nosniff / DENY / CSP headers, secrets only from env.
