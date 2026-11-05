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
1. New project → Deploy from GitHub repo (this repo, branch `main`).
   Build settings: Dockerfile path `detailing_crm/Dockerfile`, build
   context = repo root (the Dockerfile copies the frontend in).
2. Add a PostgreSQL service to the same project.
3. Env on the app service:
   - `DATABASE_URL` — the Postgres service's connection string with the
     scheme changed to `postgresql+asyncpg://` (Railway hands out
     `postgresql://`; asyncpg requires the explicit driver scheme).
   - `EXTRA_ALLOWED_HOSTS` — the generated `*.up.railway.app` domain, so
     the app answers on it before the custom domain is attached
     (TrustedHost otherwise allows only clintondetail.com / localhost).
   - `TWILIO_*` — when the Twilio checklist below is done.
4. Tables are created automatically at startup (`create_tables` in the
   app lifespan; idempotent). No manual migration step for first deploy.
5. Verify: `GET https://<generated-domain>/health` → status online.
6. Cutover: attach custom domains `clintondetail.com` + `www` in Railway,
   then point DNS at the registrar to the Railway target. After DNS
   propagates, EXTRA_ALLOWED_HOSTS can be removed.

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
