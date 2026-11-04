# Roadmap — Keeping the Calendar Full

## Phase 0 — Built in this repo (2026-11-04)
Booking engine, vehicle-first CRM schema, quote calculator, overlap-safe
calendar, lead/missed-call/SMS webhooks, nurture + reactivation logic,
review-at-completion, frontend booking form, Docker Compose, CI tests.

## Phase 1 — Go live (owner actions + wiring)
1. Host the API (Railway/VPS — see DEPLOY.md), point clintondetail.com form at it.
2. Twilio: buy/verify the shop number, register A2P 10DLC (brand + campaign),
   set TWILIO_* env. Until this is done, SMS honestly reports not-sent.
3. Scheduler job for reminders/reactivation (cron hitting a small runner
   that uses services/nurture.py due-lists, then services/sms.py).
4. Meta: create the Lead Ads webhook subscription + verify token; Google
   Business Profile messaging routed to the same lead-capture endpoint.

## Phase 2 — Conversion upgrades (from the teardown)
- Photo/condition intake on the booking form (interior shots, pet/smoke
  flags) so quotes price condition.
- Google Calendar two-way sync for the owner's phone view.
- No-show win-back sequence + one-tap reschedule link in reminders.
- Review routing: unhappy replies go private + owner alert before Google.

## Phase 3 — Lead generation (the part ads actually sell)
- Meta/Google local ads driving to the booking form (creative = before/afters,
  5-star proof — say "5 stars", never a decimal, per the owner's FB rule).
- Marketplace + Google Business Profile as free channels, same pipeline.
- Fleet/dealer outreach list for Clinton/Quad Cities with per-fleet pricing.

## Capacity truth
One bay, ~4–8h jobs = 1–2 cars/day. "Full calendar" at this scale is
~10–14 jobs/week. Growth past that is a second tech/bay decision, not software.
