"""SMS dispatch.

Honest by design: returns False until Twilio credentials are configured.
When configured, sends via the Twilio Messages REST API using httpx
(no credentials are ever hardcoded or logged).
"""
import logging
import httpx
from app.core.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER
logger = logging.getLogger(__name__)

async def send_instant_sms(to: str, message: str) -> bool:
    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_FROM_NUMBER):
        logger.warning("SMS not sent: Twilio is not configured")
        return False
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(url, data={"From": TWILIO_FROM_NUMBER, "To": to, "Body": message},
                                  auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
        if r.status_code in (200, 201):
            return True
        logger.warning("Twilio send failed: HTTP %s", r.status_code)
        return False
    except Exception:
        logger.exception("Twilio send error")
        return False
