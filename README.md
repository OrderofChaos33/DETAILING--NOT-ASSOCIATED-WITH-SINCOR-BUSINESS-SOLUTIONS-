# Clinton Auto Detailing — Booking & Lead Engine

Frictionless booking for **clintondetail.com** (715 Park Place, Clinton, IA):
a client enters name, phone, vehicle and service, the bay slot locks
instantly, and a confirmation text goes out. **No deposit, no payment gate**
— owner's explicit decision 2026-11-04, superseding the earlier deposit
draft from the same brainstorm. No payment code ships in this repo.

This is a Clinton Auto Detailing project only. It is **not associated with
SINCOR Business Solutions** — separate business, separate repo, separate voice.

## What's in here

- `docs/REVERSE_ENGINEERING_TEARDOWN.md` — clean-room teardown of the paid
  detailing software / agency systems advertising "$70k/month on autopilot"
  style claims: what they actually sell, feature by feature.
- `docs/ARCHITECTURE.md` — the full lead → booked → completed → reviewed →
  reactivated stack design.
- `docs/BUILD_ROADMAP.md` — what is built, what goes live next, capacity truth.
- `docs/DEPLOY.md` — hosting, Twilio A2P, and Meta webhook checklists.
- `detailing_crm/` — FastAPI backend: vehicle-first PostgreSQL schema
  (clients → vehicles → appointments, leads), dynamic size-based quoting,
  duration+buffer bay calendar, lead / missed-call / inbound-SMS webhooks,
  nurture + reactivation logic, review request at completion, production
  security config (TrustedHost, CORS whitelist, HSTS/nosniff/DENY, docs off).
- `frontend/` — premium mobile-first site for clintondetail.com (index.html +
  styles.css + app.js, no inline scripts so the strict CSP holds): hero with
  the $250 Full Detail, 5 stars, free pickup & delivery in Clinton/Fulton,
  licensed & insured, text Court 815-718-8936; 3-step booking (service →
  day/time from live availability → name/phone/vehicle) with live vehicle-size
  quotes and an instant confirmation screen. No account, no deposit. The
  FastAPI app serves it same-origin at `/` when the folder is present.
- `tests/` — pytest suite for pricing, calendar overlap, nurture timing, and the API.
- `docker-compose.yml` — Postgres + API for local/VPS runs.

## Honest status

- **CI workflow not in this repo yet:** `.github/workflows/ci.yml` exists in
  the local source tree but was excluded from the GitHub App push — the App
  lacks Workflows permission and GitHub rejects any tree containing a
  workflow file. Add it once via the GitHub web UI (or grant the App the
  Workflows permission) and CI runs on every push.

- **Code is built and tested; it is not yet hosted/live on clintondetail.com.**
  Deploying is a separate step (see docs/DEPLOY.md).
- **SMS sends for real only after Twilio credentials + A2P 10DLC are set.**
  Until then the API truthfully returns `sms_sent: false`.
- **No revenue claims.** The "$70,000/month on autopilot" lines are advertisers'
  claims examined in the teardown, not results or promises of this stack.

## Run locally

```bash
cp .env.example .env
docker compose up -d --build        # or: pip install -r detailing_crm/requirements.txt
curl localhost:8000/health
```

Tests: `pip install -r detailing_crm/requirements-test.txt && python -m pytest tests -q`
