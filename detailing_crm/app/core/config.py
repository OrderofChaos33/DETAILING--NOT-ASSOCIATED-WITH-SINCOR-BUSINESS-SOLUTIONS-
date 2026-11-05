"""Configuration for the Clinton Auto Detailing booking engine.

All secrets come from the environment. Nothing here hardcodes a database
password or a messaging credential. See .env.example at the repo root.
"""

import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://localhost:5432/clintondetail_db",
)

# Deploy-time host additions (comma-separated), e.g. the platform domain a
# host like Railway assigns before the custom domain is pointed at the
# service. The owner's canonical hosts stay hardcoded in app/main.py; this
# only APPENDS hosts named explicitly in the environment.
EXTRA_ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get("EXTRA_ALLOWED_HOSTS", "").split(",") if h.strip()
]

# Create model tables at startup when they do not exist yet, so a fresh
# deploy against an empty database is usable immediately. Idempotent;
# set to "false" once real migrations (Alembic) own the schema.
CREATE_TABLES_ON_STARTUP = os.environ.get(
    "CREATE_TABLES_ON_STARTUP", "true"
).strip().lower() in ("1", "true", "yes", "on")

# Twilio is a hook, not a live integration, until credentials are configured.
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.environ.get("TWILIO_FROM_NUMBER")

SHOP_NAME = "Clinton Auto Detailing"
SHOP_ADDRESS = "715 Park Place, Clinton, IA"
SHOP_DOMAIN = "clintondetail.com"
