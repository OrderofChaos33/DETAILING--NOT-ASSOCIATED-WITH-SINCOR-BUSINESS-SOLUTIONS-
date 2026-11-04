# Deploy — clintondetail.com booking engine

Pushing this repo stores code. It does NOT deploy anything by itself.

## Option A — Docker Compose (VPS)
1. Copy `.env.example` to `.env`, set a real POSTGRES_PASSWORD and Twilio values.
2. `docker compose up -d --build`
3. Create tables (first run): run a one-off python shell with
   `Base.metadata.create_all` via an async engine, or add Alembic before
   real customer data exists (recommended before Phase 1 traffic).
4. Put Caddy/Nginx in front with TLS for clintondetail.com → localhost:8000.

## Option B — Railway (or similar PaaS)
1. New service from this repo, root `detailing_crm`, add a Postgres plugin.
2. Env: DATABASE_URL (from the plugin, `postgresql+asyncpg://…`), TWILIO_*.
3. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Twilio checklist (required for real SMS)
- [ ] Account + shop number (local 815 or toll-free)
- [ ] A2P 10DLC brand + campaign registration approved (else carriers filter)
- [ ] Messaging service / From number set in env
- [ ] Inbound SMS webhook → `POST /api/v1/webhooks/sms-inbound`
- [ ] Voice missed-call flow → `POST /api/v1/webhooks/missed-call`
- [ ] Test: book from the frontend, confirm the text arrives, reply STOP, confirm opt-out

## Meta Lead Ads checklist
- [ ] Meta app + Page subscription for leadgen, webhook → `/api/v1/webhooks/lead-capture`
- [ ] Map Meta fields (phone, name, vehicle, service interest) to the payload schema
- [ ] Privacy policy URL on clintondetail.com (required by Meta + good practice)

## Compliance notes
SMS only to people who asked / booked; every automated text identifies the
shop; STOP is honored in code; calling/texting windows 8am–8pm local for
outbound nurture; keep consent records (lead raw_payload + timestamps).
